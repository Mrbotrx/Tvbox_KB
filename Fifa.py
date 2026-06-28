import os
import requests

OUTPUT_FILE = "Fifa_world_cup_pro.m3u"


def get_playlist():
    url = os.environ.get("PLAYLIST_URL")

    if not url:
        raise Exception("PLAYLIST_URL missing")

    r = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    r.raise_for_status()
    return r.text


def clean_m3u(data):
    lines = data.splitlines()

    output = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove playlist comment/header lines
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


def save_file(data):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write("#EXTM3U\n")
        f.write(data)


def main():

    print("Downloading playlist...")

    playlist = get_playlist()

    cleaned = clean_m3u(playlist)

    save_file(cleaned)

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
