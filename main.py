import os
import re
import sys
import logging
import requests

from pathlib import Path
from urllib.parse import urljoin, urlparse
from html import unescape

# ==========================================
# CONFIGURATION
# ==========================================

WEBSITE_URL = "https://ashtv.com.bd/"

OUTPUT_FILE = Path("public/ash-tv.m3u")

TIMEOUT = 25

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 "
        "Mobile Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml"
}

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

# ==========================================
# FETCH PUBLIC HTML
# ==========================================

def fetch_website():

    print(f"[WEBSITE] {WEBSITE_URL}")
    print(f"[SCANNING] {WEBSITE_URL}")

    try:

        response = requests.get(
            WEBSITE_URL,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        if "text/html" not in response.headers.get(
            "Content-Type", ""
        ).lower():

            print("[WARNING] Response is not HTML")
            return None

        return response.text

    except requests.RequestException as error:

        print(f"[ERROR] Website request failed: {error}")

        return None


# ==========================================
# FIND PUBLIC M3U8 LINKS
# ==========================================

def extract_public_streams(html):

    if not html:
        return []

    html = unescape(html)

    patterns = [

        r"""["']([^"'<>]+\.m3u8(?:\?[^"'<>]*)?)["']""",

        r"""(?:src|href)\s*=\s*["']([^"']+\.m3u8(?:\?[^"']*)?)["']""",

    ]

    found = set()

    for pattern in patterns:

        matches = re.findall(
            pattern,
            html,
            re.IGNORECASE
        )

        for match in matches:

            url = urljoin(WEBSITE_URL, match.strip())

            parsed = urlparse(url)

            if parsed.scheme not in ("http", "https"):
                continue

            if not parsed.path.lower().endswith(".m3u8"):
                continue

            found.add(url)

    return sorted(found)


# ==========================================
# BUILD M3U PLAYLIST
# ==========================================

def build_playlist(streams):

    lines = ["#EXTM3U"]

    for index, stream in enumerate(streams, start=1):

        name = f"ASH TV Channel {index}"

        lines.append(
            f'#EXTINF:-1 tvg-name="{name}" '
            f'group-title="ASH TV",{name}'
        )

        lines.append(stream)

    return "\n".join(lines) + "\n"


# ==========================================
# SAFE FILE UPDATE
# ==========================================

def save_playlist(streams):

    # IMPORTANT:
    # Never overwrite an existing playlist
    # when no new streams are discovered.

    if not streams:

        print("[FOUND] 0")

        if OUTPUT_FILE.exists():

            print("[KEEP] Previous playlist preserved.")

        else:

            print("[INFO] No previous playlist exists.")

        print("[SUCCESS] Nothing to update.")
        return True

    try:

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        playlist = build_playlist(streams)

        temporary_file = OUTPUT_FILE.with_suffix(
            OUTPUT_FILE.suffix + ".tmp"
        )

        temporary_file.write_text(
            playlist,
            encoding="utf-8"
        )

        # Atomic replacement
        temporary_file.replace(OUTPUT_FILE)

        print(f"[FOUND] {len(streams)}")

        print(f"[SAVED] {OUTPUT_FILE}")

        print("[SUCCESS] Playlist updated.")

        return True

    except OSError as error:

        print(f"[ERROR] File update failed: {error}")

        return False


# ==========================================
# MAIN
# ==========================================

def main():

    print("=" * 45)
    print("ASH TV M3U8 PLAYLIST GENERATOR")
    print("=" * 45)

    html = fetch_website()

    if html is None:

        print("[WARNING] Website unavailable.")
        print("[KEEP] Existing playlist preserved.")

        # Do not fail GitHub Actions
        return 0

    streams = extract_public_streams(html)

    print(f"[FOUND] {len(streams)}")

    result = save_playlist(streams)

    if not result:

        print("[WARNING] Playlist update unsuccessful.")

        return 0

    print("=" * 45)
    print("PROCESS COMPLETED")
    print("=" * 45)

    return 0


if __name__ == "__main__":

    sys.exit(main())
