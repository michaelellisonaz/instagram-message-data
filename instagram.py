#!/usr/bin/env python3
"""
Instagram DM Export Cleaner (HTML → TXT)

Features:
- Reads message_*.html files from Instagram export
- Extracts human-written messages only
- Optionally keeps Instagram links as [reel: URL]
- Outputs ONE clean text file

Usage:
  pip install beautifulsoup4 lxml
  python ig_dm_cleaner.py
"""

import glob
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup

# ---------------- CONFIG ----------------
PARTICIPANTS = {"Participant A", "Participant B"}  # change to display names
INPUT_GLOB = "message_*.html"
OUTPUT_FILE = "messages_clean.txt"

INCLUDE_IG_LINKS = True
LINK_LABEL = "reel"

# ---------------- HELPERS ----------------
def parse_timestamp(ts: str):
    for fmt in ("%b %d, %Y %I:%M %p", "%b %d, %Y %I:%M%p"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            pass
    return None


def normalize_instagram_url(url: str):
    if "instagram.com" not in url:
        return None
    parsed = urlparse(url)
    return f"https://{parsed.netloc}{parsed.path}"


def extract_links(container):
    links = []
    for a in container.find_all("a", href=True):
        clean = normalize_instagram_url(a["href"])
        if clean and clean not in links:
            links.append(clean)
    return links


def extract_text(container):
    parts = []
    for div in container.find_all("div", recursive=True):
        text = div.get_text(" ", strip=True)
        if not text:
            continue

        lower = text.lower()

        if text.endswith("sent an attachment."):
            continue
        if lower.startswith("cr: @") or "#" in text:
            continue
        if " " not in text and ("@" in text or text.islower()):
            continue

        parts.append(text)

    return parts


_REPEAT_RE = re.compile(r"^(?P<t>.+?) \1$")

def dedupe_text(text: str) -> str:
    text = text.strip()
    m = _REPEAT_RE.match(text)
    return m.group("t") if m else text


@dataclass
class Message:
    dt: datetime | None
    timestamp: str
    sender: str
    text: str


# ---------------- CORE ----------------
def parse_html(path: str):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    messages = []

    for block in soup.find_all("div", class_="pam"):
        name_tag = block.find("h2")
        if not name_tag:
            continue

        sender = name_tag.get_text(strip=True)
        if sender not in PARTICIPANTS:
            continue

        time_tag = block.find("div", class_="_3-94 _a6-o")
        timestamp = time_tag.get_text(strip=True) if time_tag else ""
        dt = parse_timestamp(timestamp)

        container = block.find("div", class_="_3-95 _a6-p")
        if not container:
            continue

        chunks = []

        text_parts = extract_text(container)
        if text_parts:
            chunks.append(" ".join(text_parts))

        if INCLUDE_IG_LINKS:
            for link in extract_links(container):
                chunks.append(f"[{LINK_LABEL}: {link}]")

        if not chunks:
            continue

        final_text = dedupe_text(" ".join(chunks))
        messages.append(Message(dt, timestamp, sender, final_text))

    return messages


def main():
    files = sorted(glob.glob(INPUT_GLOB))
    if not files:
        raise SystemExit("No message_*.html files found.")

    all_msgs = []
    for f in files:
        print(f"Processing {f}...")
        all_msgs.extend(parse_html(f))

    all_msgs.sort(key=lambda m: (m.dt is None, m.dt))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for m in all_msgs:
            out.write(f"{m.timestamp} - {m.sender}: {m.text}\n")

    print(f"\nDone! Clean export written to: {OUTPUT_FILE}")
    print(f"Total messages: {len(all_msgs)}")


if __name__ == "__main__":
    main()
