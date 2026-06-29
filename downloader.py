import os
import requests
from datetime import datetime

OUTPUT_FILE = "newtv.m3u"


def download_m3u():
    url = os.environ.get("VPN_URL")

    if not url:
        print("ERROR: VPN_URL secret missing")
        return

    print("IPTV BOT X KB")
    print("Downloading playlist...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

        # Read playlist
        playlist = response.text

        # Split into lines
        lines = playlist.splitlines()

        # Find first channel (#EXTINF)
        start = 0
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF"):
                start = i
                break

        # Keep only channels
        channels = lines[start:]

        # Count channels
        channel_count = sum(
            1 for line in channels
            if line.startswith("#EXTINF")
        )

        # Current date & time
        update_time = datetime.now().strftime("%I:%M %p %d-%m-%Y")

        # Create new header
        header = [
            "#EXTM3U",
            "#PLAYLIST: IPTV BOT X KB",
            "#EXTENC: UTF-8",
            "",
            "# Playlist Name: IPTV BOT X KB",
            f"# Total Channels: {channel_count}",
            f"# Last Update: {update_time}",
            ""
        ]

        # Final playlist
        final_playlist = "\n".join(header + channels)

        # Save file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_playlist)

        print("===================================")
        print("Download Complete!")
        print(f"Saved As      : {OUTPUT_FILE}")
        print(f"Total Channels: {channel_count}")
        print(f"Last Update   : {update_time}")
        print("===================================")

    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    download_m3u()
