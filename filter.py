import requests
import os
from concurrent.futures import ThreadPoolExecutor

# =========================
# 🔥 KB TV PRO ADVANCED HEADER
# =========================
print("\033[95m" + "="*60)
print("        KB TV PRO ADVANCED FILTER SYSTEM V3")
print("     BANGLADESH 🇧🇩 + INDIA 🇮🇳 SMART ENGINE")
print("="*60 + "\033[0m")

SOURCE_URL = os.getenv("SOURCE_URL")
OUTPUT_FILE = "kb_tv.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

# =========================
# SMART CHANNEL DATABASE
# =========================
BD_CHANNELS = [
    "channel i", "gtv", "ntv", "atn bangla",
    "somoy tv", "ekattor tv", "jamuna tv",
    "desh tv", "boishakhi tv", "deepto tv",
    "mohona tv", "banglavision", "mytv",
    "news24", "dbc news", "rtv"
]

INDIA_CHANNELS = [
    "sony", "sony liv", "zee", "zee tv", "zee cinema",
    "star plus", "star gold", "star sports",
    "colors tv", "colors", "sun tv", "vijay tv",
    "discovery", "nat geo", "animal planet",
    "mtv india"
]

KEYWORDS = BD_CHANNELS + INDIA_CHANNELS

BLOCK_WORDS = [
    "movie", "vod", "trailer", "promo",
    ".mp4", ".mkv", ".avi", ".mov",
    "sample", "test", "ad", "demo",
    "backup", "playlist"
]

# =========================
# FAST PARSER
# =========================
def parse_m3u(data):
    lines = data.splitlines()
    return [
        (lines[i], lines[i + 1])
        for i in range(len(lines) - 1)
        if lines[i].startswith("#EXTINF")
    ]


# =========================
# FILTER ENGINE
# =========================
def is_valid(text):
    text = text.lower()
    return any(k in text for k in KEYWORDS)


def is_blocked(text):
    text = text.lower()
    return any(b in text for b in BLOCK_WORDS)


# =========================
# LIVE CHECK (SMART)
# =========================
def check_live(url):
    try:
        r = requests.head(url, timeout=4, allow_redirects=True)
        return r.status_code in [200, 206]
    except:
        return False


# =========================
# MAIN ENGINE
# =========================
def main():

    if not SOURCE_URL:
        print("❌ SOURCE_URL missing")
        return

    print("📥 Fetching playlist...")

    try:
        data = requests.get(SOURCE_URL, headers=HEADERS, timeout=20).text
    except Exception as e:
        print("❌ Error:", e)
        return

    channels = parse_m3u(data)

    print(f"📊 Total Channels: {len(channels)}")

    filtered = []
    seen = set()

    # =========================
    # FILTER STEP
    # =========================
    for extinf, url in channels:

        if url in seen:
            continue

        full = (extinf + url).lower()

        if is_blocked(full):
            continue

        if not is_valid(full):
            continue

        seen.add(url)
        filtered.append((extinf, url))

    print(f"⚡ After Filter: {len(filtered)}")

    # =========================
    # SMART LIVE CHECK
    # =========================
    print("🚀 Checking live streams (advanced mode)...")

    working = []

    with ThreadPoolExecutor(max_workers=80) as pool:
        results = list(pool.map(lambda x: (x, check_live(x[1])), filtered))

    for (extinf, url), ok in results:
        if ok:
            working.append((extinf, url))
            print("✅ LIVE:", extinf[:60])

    # =========================
    # OUTPUT GENERATION
    # =========================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("# KB TV PRO ADVANCED ENGINE V3\n")
        f.write("# REGION: BD + INDIA\n")
        f.write(f"# TOTAL: {len(working)} CHANNELS\n\n")

        for extinf, url in working:
            f.write(extinf + "\n")
            f.write(url + "\n")

    # =========================
    # TERMINAL END
    # =========================
    print("\033[96m")
    print("="*60)
    print("   KB TV PRO ADVANCED FILTER COMPLETED")
    print(f"   WORKING CHANNELS: {len(working)}")
    print("="*60)
    print("\033[0m")


if __name__ == "__main__":
    main()
