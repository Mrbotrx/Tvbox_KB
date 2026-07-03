import os
import requests
import json
from datetime import datetime
from telegram import Telegram

INPUT_URL = os.getenv("INPUT_URL")

def fetch(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text.splitlines()

def process(lines):
    m3u = ["#EXTM3U"]
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

                json_data.append({"title": title, "url": line})
                count += 1
                title = None

    return m3u, json_data, count

def main():
    os.makedirs("output", exist_ok=True)

    bot = Telegram()

    print("[+] Fetching playlist...")
    lines = fetch(INPUT_URL)

    print("[+] Processing...")
    m3u, json_data, count = process(lines)

    m3u_file = "output/bd_fifa.m3u8"
    json_file = "output/channels.json"

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    caption = f"🔥 KB TV PRO\n📺 Channels: {count}\n⏰ {datetime.utcnow()}"

    # safer chat detection
    updates = bot.get_updates()
    chat_id = None

    if updates and updates.get("result"):
        try:
            chat_id = updates["result"][-1]["message"]["chat"]["id"]
        except:
            pass

    if chat_id:
        print("[+] Sending Telegram...")
        bot.send_message(chat_id, caption)
        bot.send_file(chat_id, m3u_file, "M3U Playlist")
        bot.send_file(chat_id, json_file, "JSON Data")
    else:
        print("[!] No chat_id found. Send message to bot first.")

if __name__ == "__main__":
    main()
