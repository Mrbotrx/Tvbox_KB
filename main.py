import json
import re
import requests

from urllib.parse import urljoin, urlparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def load_config():
    with open("config.json", encoding="utf-8") as f:
        return json.load(f)


def fetch(url):
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print("[ERROR]", e)
        return None


def extract_links(html, base):
    soup = BeautifulSoup(html, "html.parser")

    results = {}

    for tag in soup.find_all(["a", "video", "source"]):

        link = tag.get("href") or tag.get("src")

        if not link:
            continue

        if ".m3u8" not in link.lower():
            continue

        link = urljoin(base, link)

        name = (
            tag.get("title")
            or tag.get("aria-label")
            or tag.get_text(strip=True)
            or "Unknown Channel"
        )

        results[link] = name

    pattern = r'https?://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?'

    for link in re.findall(pattern, html, re.I):
        results.setdefault(link.rstrip("),;"), "Unknown Channel")

    return results


def scan_website(start_url, max_pages):

    domain = urlparse(start_url).netloc

    visited = set()
    pending = [start_url]
    channels = {}

    while pending and len(visited) < max_pages:

        url = pending.pop(0)

        if url in visited:
            continue

        visited.add(url)

        html = fetch(url)

        if not html:
            continue

        channels.update(
            extract_links(html, url)
        )

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all("a", href=True):

            link = urljoin(url, tag["href"])

            parsed = urlparse(link)

            if (
                parsed.scheme in ("http", "https")
                and parsed.netloc == domain
                and link not in visited
                and link not in pending
            ):
                pending.append(link)

    return channels


def detect_category(name, url, categories):

    text = (name + " " + url).lower()

    for category, keywords in categories.items():

        if category == "Others":
            continue

        if any(k.lower() in text for k in keywords):
            return category

    return "Others"


def check_stream(url):

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
            stream=True
        )

        if r.status_code != 200:
            r.close()
            return False

        content = next(
            r.iter_content(2048),
            b""
        )

        content_type = r.headers.get(
            "Content-Type", ""
        ).lower()

        r.close()

        return (
            b"#EXTM3U" in content
            or "mpegurl" in content_type
        )

    except requests.RequestException:
        return False


def create_playlist(channels, config):

    groups = defaultdict(list)

    for url, name in channels.items():

        category = detect_category(
            name,
            url,
            config["categories"]
        )

        groups[category].append((name, url))

    lines = ["#EXTM3U"]

    for category in config["categories"]:

        for name, url in sorted(groups[category]):

            name = name.replace('"', "'")

            lines.append(
                f'#EXTINF:-1 group-title="{category}",{name}'
            )

            lines.append(url)

    with open(
        config["output"],
        "w",
        encoding="utf-8"
    ) as f:
        f.write("\n".join(lines) + "\n")

    print("[SUCCESS] Playlist created")


def main():

    config = load_config()

    channels = {}

    for website in config["source_urls"]:

        print("[SCANNING]", website)

        channels.update(
            scan_website(
                website,
                config["max_pages"]
            )
        )

    print("[FOUND]", len(channels))

    if not channels:
        print("[INFO] No public M3U8 URLs found.")
        return

    urls = list(channels)

    with ThreadPoolExecutor(
        max_workers=config["max_workers"]
    ) as executor:

        statuses = list(
            executor.map(check_stream, urls)
        )

    working = {}

    for url, status in zip(urls, statuses):

        if status:
            working[url] = channels[url]
            print("[WORKING]", channels[url])
        else:
            print("[INVALID]", channels[url])

    create_playlist(working, config)


if __name__ == "__main__":
    main()
