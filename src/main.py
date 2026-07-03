import os
import requests
import json
from telegram import Telegram
from datetime import datetime

INPUT_URL = os.getenv("INPUT_URL")

def fetch(url):
    return requests.get(url, timeout=20).text.splitlines()

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
    bot = Telegram()

    updates = bot.get_updates()

    if not updates or "result" not in updates:
        print("No updates")
        return

    for u in updates["result"]:
        try:
            msg = u["message"]["text"]
            chat_id = u["message"]["chat"]["id"]

            # 👉 START COMMAND
            if msg == "/start":
                print("[+] Start command detected")

                lines = fetch(INPUT_URL)
                m3u, json_data, count = process(lines)

                os.makedirs("output", exist_ok=True)

                m3u_file = "output/bd_fifa.m3u8"
                json_file = "output/channels.json"

                with open(m3u_file, "w") as f:
                    f.write("\n".join(m3u))

                with open(json_file, "w") as f:
                    json.dump(json_data, f, indent=2)

                caption = f"""🔥 KB TV PRO
📺 Channels: {count}
⏰ {datetime.utcnow()}"""

                bot.send_message(chat_id, "🚀 Generating playlist...")
                bot.send_file(chat_id, m3u_file, "M3U Playlist")
                bot.send_file(chat_id, json_file, "Channels JSON")

        except:
            continue

if __name__ == "__main__":
    main()
