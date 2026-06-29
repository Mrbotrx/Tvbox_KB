import os
import requests

OUTPUT_FILE = "Fifa_world_cup_pro.m3u"


def get_playlist():
    url = os.environ.get("PLAYLIST_URL")

    if not url:
        raise RuntimeError("PLAYLIST_URL environment variable is missing.")

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()
    return response.text


def clean_m3u(data):
    output = []

    for line in data.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove unwanted comments
        if line.startswith("#PLAYLIST:"):
            continue
        if line.startswith("#EXTENC:"):
            continue
        if line.startswith("# Playlist"):
            continue
        if line.startswith("# Last Update:"):
            continue
        if line.startswith("# Facebook"):
            continue
        if line.startswith("# Fb Page"):
            continue
        if line.startswith("# This link"):
            continue

        output.append(line)

    return "\n".join(output)


def save_playlist(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("#EXTM3U\n")
        file.write(data)
        file.write("\n")


def main():
    print("Downloading playlist...")

    playlist = get_playlist()

    print("Cleaning playlist...")

    cleaned = clean_m3u(playlist)

    save_playlist(cleaned)

    print(f"Done! Saved as {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
