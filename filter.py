import requests
import os
from concurrent.futures import ThreadPoolExecutor

SOURCE_URL = os.getenv("SOURCE_URL")
OUTPUT_FILE = "kb_tv.m3u"

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# BD + INDIA CHANNEL FILTER
# =========================
BD_IN_KEYWORDS = [
    "bangla", "bangladesh", "bd",
    "india", "in ", "hindi",
    "channel i", "gtv", "ntv",
    "atn", "somoy", "ekattor",
    "jamuna", "desh tv",
    "boishakhi", "deepto",
    "sony", "zee", "star",
    "colors", "sun tv"
]

BLOCK_WORDS = [
    "movie", "vod", "trailer", "promo",
    ".mp4", ".mkv", ".avi", ".mov",
    "sample", "test", "ad", "advert"
]


# =========================
# CHECK FUNCTIONS
# =========================
def is_valid_channel(text):
    text = text.lower()
    return any(k in text for k in BD_IN_KEYWORDS)


def is_blocked(text):
    text = text.lower()
    return any(b in text for b in BLOCK_WORDS)


def parse_m3u(data):
    lines = data.splitlines()
    items = []

    for i in range(len(lines) - 1):
        if lines[i].startswith("#EXTINF"):
            items.append((lines[i], lines[i + 1]))
    return items


def check_live(url):
    try:
        r = requests.head(url, timeout=6, allow_redirects=True)
        return r.status_code in [200, 206]
    except:
        return False


# =========================
# MAIN PROCESS
# =========================
def main():
    if not SOURCE_URL:
        print("ERROR: SOURCE_URL not set")
        return

    print("Downloading playlist...")

    try:
        data = requests.get(SOURCE_URL, headers=HEADERS, timeout=25).text
    except Exception as e:
        print("Download failed:", e)
        return

    channels = parse_m3u(data)
    print("Total Channels Found:", len(channels))

    filtered = []
    seen = set()

    for extinf, url in channels:
        if url in seen:
            continue

        if is_blocked(extinf + url):
            continue

        if not is_valid_channel(extinf):
            continue

        seen.add(url)
        filtered.append((extinf, url))

    print("Filtered Channels:", len(filtered))

    print("Checking live streams (fast mode)...")

    working = []

    with ThreadPoolExecutor(max_workers=60) as executor:
        results = list(executor.map(lambda x: (x, check_live(x[1])), filtered))

    for (extinf, url), ok in results:
        if ok:
            working.append((extinf, url))

    print("Working Channels:", len(working))

    # =========================
    # WRITE OUTPUT
    # =========================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Generated: Auto Filter System\n")
        f.write(f"# Total Channels: {len(working)}\n\n")

        for extinf, url in working:
            f.write(extinf + "\n")
            f.write(url + "\n")

    print("DONE ->", OUTPUT_FILE)


if __name__ == "__main__":
    main()
