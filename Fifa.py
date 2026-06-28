import os
import requests

OUTPUT_FILE = "Fifa_world_cup_pro.m3u"

def get_playlist():
    url = os.environ.get("PLAYLIST_URL")

    if not url:
        raise Exception("PLAYLIST_URL secret missing")

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    return response.text


def save_playlist(data):
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(data)


def main():
    print("Downloading authorized playlist...")

    playlist = get_playlist()

    save_playlist(playlist)

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
