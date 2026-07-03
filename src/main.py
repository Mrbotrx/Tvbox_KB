import requests
import os
import json

INPUT_URL = os.getenv("INPUT_URL")

M3U_OUT = "output/bd_fifa.m3u8"
JSON_OUT = "output/channels.json"

def fetch(url):
    return requests.get(url, timeout=20).text.splitlines()

def is_valid(line):
    return line and not line.startswith("#")

def process(lines):
    m3u = []
    json_list = []

    current_title = None

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            current_title = line
            continue

        if is_valid(line):
            # save m3u
            m3u.append(current_title)
            m3u.append(line)

            # save json
            json_list.append({
                "title": current_title,
                "url": line
            })

            current_title = None

    return m3u, json_list

def save_m3u(data):
    with open(M3U_OUT, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("\n".join(data))

def save_json(data):
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    print("Fetching playlist...")
    lines = fetch(INPUT_URL)

    print("Processing channels...")
    m3u, json_data = process(lines)

    print("Saving outputs...")
    os.makedirs("output", exist_ok=True)

    save_m3u(m3u)
    save_json(json_data)

    print("Done!")

if __name__ == "__main__":
    main()
