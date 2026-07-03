import os
import requests
import json
from datetime import datetime
from telegram import Telegram

INPUT_URL = os.getenv("INPUT_URL")

M3U_FILE = "output/bd_fifa.m3u8"
JSON_FILE = "output/channels.json"

def fetch(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text.splitlines()

def process(lines):
    m3u = []
    json_data = []
    title = None
    count = 0

    for line in lines:
        if line.startswith("#EXTINF"):
            title = line
        elif line and not line.startswith("#"):
            if title:
                m3u.append(title)
                m3u.append(line)

                json_data.append({
                    "title": title,
                    "url": line
                })

                count += 1
                title = None

    return m3u, json_data, count

def save_m3u(path, data, count):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    header = [
        "#EXTM3U",
        "#PLAYLIST: KB TV PRO",
        f"#CREATED: {now}",
        f"#CHANNELS: {count}",
        ""
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(header + data))

def save_json(path, data, count):
    output = {
        "playlist": "KB TV PRO",
        "created": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "total_channels": count,
        "channels": data
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

def main():
    os.makedirs("output", exist_ok=True)

    bot = Telegram()

    print("[+] Fetching IPTV...")
    lines = fetch(INPUT_URL)

    print("[+] Processing...")
    m3u, json_data, count = process(lines)

    print("[+] Saving files...")
    save_m3u(M3U_FILE, m3u, count)
    save_json(JSON_FILE, json_data, count)

    caption = f"🔥 KB TV PRO\n📺 Channels: {count}\n⏰ {datetime.utcnow()}"

    # chat id from first update
    updates = bot.get_updates()
    chat_id = None

    if updates and updates.get("result"):
        try:
            chat_id = updates["result"][-1]["message"]["chat"]["id"]
        except:
            pass

    if chat_id:
        print("[+] Sending to Telegram...")
        bot.send_message(chat_id, caption)
        bot.send_file(chat_id, M3U_FILE, "M3U Playlist")
        bot.send_file(chat_id, JSON_FILE, "JSON Data")

    print("[✓] DONE")

if __name__ == "__main__":
    main()
