import requests
import os
from datetime import datetime


OUTPUT_FILE = "newtv.m3u"


def download_m3u():

    url = os.environ.get("VPN_URL")

    if not url:
        print("ERROR: VPN_URL secret missing")
        exit(1)

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

        playlist = response.text

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(playlist)


        print("---------------------------")
        print("STATUS : SUCCESS")
        print("FILE   :", OUTPUT_FILE)
        print("SIZE   :", os.path.getsize(OUTPUT_FILE), "bytes")
        print("TIME   :", datetime.now())
        print("---------------------------")


    except requests.exceptions.Timeout:
        print("ERROR: Connection timeout")
        exit(1)


    except requests.exceptions.RequestException as e:
        print("ERROR:", e)
        exit(1)



if __name__ == "__main__":
    download_m3u()
