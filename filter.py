#!/usr/bin/env python3

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

SOURCE_URL = os.environ.get("SOURCE_URL")

if not SOURCE_URL:
    raise Exception("SOURCE_URL secret not found")

OUTPUT_FILE = "kb_tv.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BLOCK_WORDS = [
    "promo",
    "trailer",
    "sample",
    "movie",
    "vod",
    "test",
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm"
]

COUNTRY_KEYWORDS = [
    # Bangladesh
    "bangla",
    "bangladesh",
    "channel i",
    "gtv",
    "atn",
    "somoy",
    "jamuna",
    "ekattor",
    "independent",
    "ntv",
    "banglavision",
    "deepto",

    # India
    "india",
    "star",
    "zee",
    "sony",
    "colors",
    "sports18",
    "star sports",
    "sony sports",
    "dd sports",
    "star jalsha",
    "zee bangla",
    "colors bangla",
    "abp",
    "news18",
    "aaj tak"
]

BEST_CHANNELS = [
    "star sports",
    "sony sports",
    "sports18",
    "dd sports",
    "channel i",
    "gtv",
    "jamuna",
    "somoy",
    "ekattor",
    "independent",
    "ntv",
    "star jalsha",
    "zee bangla",
    "colors bangla"
]


def parse_playlist(content):
    channels = []
    lines = content.splitlines()

    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            if i + 1 < len(lines):
                channels.append(
                    (lines[i].strip(), lines[i + 1].strip())
                )
            i += 2
        else:
            i += 1

    return channels


def is_blocked(name, url):
    text = (name + " " + url).lower()

    return any(word in text for word in BLOCK_WORDS)


def is_bd_india(extinf):
    text = extinf.lower()

    return any(
        keyword in text
        for keyword in COUNTRY_KEYWORDS
    )


def priority(extinf):
    text = extinf.lower()

    for index, keyword in enumerate(BEST_CHANNELS):
        if keyword in text:
            return index

    return 999


def check_stream(url):
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=8,
            stream=True,
            allow_redirects=True
        )

        return r.status_code in [200, 206]

    except:
        return False


playlist = requests.get(
    SOURCE_URL,
    headers=HEADERS,
    timeout=30
).text

channels = parse_playlist(playlist)

filtered = []
seen = set()

for extinf, url in channels:

    name = extinf.split(",")[-1]

    if is_blocked(name, url):
        continue

    if not is_bd_india(extinf):
        continue

    if url in seen:
        continue

    seen.add(url)
    filtered.append((extinf, url))

working = []

with ThreadPoolExecutor(max_workers=50) as executor:

    futures = {
        executor.submit(check_stream, url): (extinf, url)
        for extinf, url in filtered
    }

    for future in as_completed(futures):

        extinf, url = futures[future]

        try:
            if future.result():
                working.append((extinf, url))
        except:
            pass

working.sort(key=lambda x: priority(x[0]))

generated = datetime.utcnow().strftime(
    "%Y-%m-%d %H:%M:%S UTC"
)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    f.write("#EXTM3U\n")
    f.write(f"# Generated-Time: {generated}\n")
    f.write(f"# Total-Channels: {len(working)}\n")
    f.write("# Country: Bangladesh + India\n")
    f.write("# Generator: KB TV Auto Filter\n")
    f.write("# Version: 3.0\n\n")

    for extinf, url in working:
        f.write(extinf + "\n")
        f.write(url + "\n")

print(
    f"Done. Saved {len(working)} channels to {OUTPUT_FILE}"
)
