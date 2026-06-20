"""Toronto events feed builder.

Pulls upcoming Toronto events from blogTO's public RSS feed and injects a
Markdown table into docs/index.md between the <!-- START:events --> and
<!-- END:events --> markers.

History: this used to drive a headless Playwright browser against
blogto.com/events/, but blogTO now serves a bot-gate to headless Chromium
(blank page, body "Login error happened.") so that approach silently produced
nothing from ~2026-04-23 onward. The RSS feed answers a plain GET with no
gate, so we use that instead -- no browser, no Chromium-in-CI.
"""

import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape

import requests
from bs4 import BeautifulSoup

FEED_URL = "https://www.blogto.com/rss/events.xml"
INDEX_PATH = "docs/index.md"
START_MARKER = "<!-- START:events -->\n"
END_MARKER = "\n<!-- END:events -->"
# A real browser UA; the feed is ungated but some CDNs 403 the default
# python-requests UA.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
MAX_EVENTS = 25


def clean_md_cell(text):
    if not text:
        return ""
    # Remove newlines and tabs, replace with space
    text = re.sub(r"[\r\n\t]+", " ", text)
    # Replace pipe chars so they don't break the Markdown table
    text = text.replace("|", "│")
    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_feed(xml_bytes):
    """Return a list of (img_url, title, link, description) tuples."""
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        return [], None

    last_build = channel.findtext("lastBuildDate") or None

    events = []
    for item in channel.findall("item")[:MAX_EVENTS]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        raw_desc = item.findtext("description") or ""

        # The description is escaped HTML: an <img> plus <p> body.
        desc_soup = BeautifulSoup(unescape(raw_desc), "html.parser")

        img_tag = desc_soup.find("img")
        img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

        text = " ".join(desc_soup.stripped_strings)
        text = re.sub(r"\s+", " ", unescape(text)).strip()
        if len(text) > 100:
            text = text[:97] + "..."

        if title and link:
            events.append((img_url, title, link, text))

    return events, last_build


def build_table(events, last_build):
    header = (
        "| | Event | Description |\n"
        "|---|-------|-------------|"
    )
    rows = []
    for img, title, link, desc in events:
        md_img = f'<img src="{img}" width="120"/>' if img else ""
        md_link = f"[{clean_md_cell(title)}]({link})"
        rows.append(f"| {md_img} | {md_link} | {clean_md_cell(desc)} |")

    # Visible freshness stamp so the page can never silently look "live"
    # while being stale. Prefer the feed's own lastBuildDate; fall back to now.
    stamp = last_build or datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M %Z"
    )
    caption = f"*{len(events)} upcoming events · last updated {stamp} · source: [blogTO]({FEED_URL})*"

    return caption + "\n\n" + header + "\n" + "\n".join(rows)


def main():
    resp = requests.get(FEED_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    events, last_build = parse_feed(resp.content)

    # Freshness guard: never overwrite a good table with emptiness. If the
    # feed shape changes or the fetch returns nothing usable, fail loudly
    # and leave docs/index.md untouched.
    if not events:
        print("ERROR: parsed 0 events from feed; leaving index.md unchanged.",
              file=sys.stderr)
        sys.exit(1)

    table = build_table(events, last_build)

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 or end == -1:
        print(f"ERROR: markers not found in {INDEX_PATH}.", file=sys.stderr)
        sys.exit(1)
    start += len(START_MARKER)

    updated = content[:start] + "\n" + table + "\n" + content[end:]

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"Wrote {len(events)} events to {INDEX_PATH} (last updated {last_build}).")


if __name__ == "__main__":
    main()
