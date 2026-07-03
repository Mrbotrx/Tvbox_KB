import requests
import os
import json
from datetime import datetime

INPUT_URL = os.getenv("INPUT_URL")

M3U_OUT = "output/bd_fifa.m3u8"
JSON_OUT = "output/channels.json"

def fetch(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text.splitlines()

def process(lines):
    m3u_data = []
    json_data = []

    title = None
    count = 0

    for line in lines:
        if line.startswith("#EXTINF"):
            title = line
        elif line and not line.startswith("#"):
            if title:
                m3u_data.append(title)
                m3u_data.append(line)

                json_data.append({
                    "title": title,
                    "url": line
                })

                count += 1
                title = None

    return m3u_data, json_data, count

def save_m3u(path, data, count):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

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
        "created": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_channels": count,
        "channels": data
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

def main():
    os.makedirs("output", exist_ok=True)

    print("[+] Fetching playlist...")
    lines = fetch(INPUT_URL)

    print("[+] Processing channels...")
    m3u, json_data, count = process(lines)

    print(f"[+] Total channels found: {count}")

    print("[+] Saving M3U...")
    save_m3u(M3U_OUT, m3u, count)

    print("[+] Saving JSON...")
    save_json(JSON_OUT, json_data, count)

    print("[✓] KB TV PRO build complete!")

if __name__ == "__main__":
    main()
