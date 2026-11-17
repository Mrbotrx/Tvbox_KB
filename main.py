import json
import re
import requests

from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "config.json"


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def load_config():

    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def fetch(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:

        print("[ERROR]", error)

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

    pattern = (
        r'https?://[^\s"\'<>]+\.m3u8'
        r'(?:\?[^\s"\'<>]*)?'
    )

    for link in re.findall(pattern, html, re.I):

        link = link.rstrip("),;")

        results.setdefault(
            link,
            "Unknown Channel"
        )

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

        print("[SCANNING]", url)

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

        for keyword in keywords:

            if keyword.lower() in text:
                return category

    return "Others"


def check_stream(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
            stream=True
        )

        if response.status_code != 200:

            response.close()

            return False

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        data = next(
            response.iter_content(2048),
            b""
        )

        response.close()

        return (
            b"#EXTM3U" in data
            or "mpegurl" in content_type
        )

    except requests.RequestException:

        return False


def create_playlist(channels, config):

    groups = defaultdict(list)

    categories = config["categories"]

    for url, name in channels.items():

        category = detect_category(
            name,
            url,
            categories
        )

        groups[category].append(
            (name, url)
        )

    lines = ["#EXTM3U"]

    for category in categories:

        items = groups.get(category, [])

        for name, url in sorted(items):

            name = name.replace('"', "'")

            lines.append(
                f'#EXTINF:-1 group-title="{category}",{name}'
            )

            lines.append(url)

    output_file = BASE_DIR / config["output"]

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(lines) + "\n"
        )

    print("[SUCCESS] Playlist created:", output_file)

    print("[TOTAL CHANNELS]", len(channels))


def main():

    config = load_config()

    all_channels = {}

    for website in config["source_urls"]:

        print("\n[WEBSITE]", website)

        channels = scan_website(
            website,
            config["max_pages"]
        )

        all_channels.update(channels)

    print("\n[FOUND]", len(all_channels))

    if not all_channels:

        raise RuntimeError(
            "No publicly exposed M3U8 links found."
        )

    urls = list(all_channels.keys())

    with ThreadPoolExecutor(
        max_workers=config["max_workers"]
    ) as executor:

        results = list(
            executor.map(check_stream, urls)
        )

    working = {}

    for url, status in zip(urls, results):

        if status:

            working[url] = all_channels[url]

            print("[WORKING]", all_channels[url])

        else:

            print("[INVALID]", all_channels[url])

    if not working:

        raise RuntimeError(
            "No working M3U8 streams found."
        )

    create_playlist(
        working,
        config
    )


if __name__ == "__main__":

    main()
