#!/usr/bin/env python3
"""Refresh the citation counts shown on the Researcher page.

Asks Google Scholar for the profile page, picks out the papers listed in PAPERS and writes their "Cited by"
counts to a JSON file. The citation badges on the Researcher page read that file.

Usage: update_citations.py <citations.json>

The request says openly that it comes from a script, and it asks for a page that Scholar's robots.txt allows.
Google Scholar turns away many of GitHub's machines all the same (HTTP 403). The counts then stay as they
are and the next day's run asks again; the script makes no attempt to get around a refusal. Only when no
answer has come for STALE_DAYS days does it fail, so that GitHub sends a notice.
"""
import datetime
import gzip
import http.client
import json
import re
import sys
import urllib.error
import urllib.request
import zlib

USER = "REtoPf8AAAAJ"
# JSON key -> the paper's id on the Scholar profile (what follows "citation_for_view=USER:" in its link).
PAPERS = {
    "amphion": "d1gkVwhDpl0C",
    "yue2": "YOwf2qJgpHMC",
    "foleycrafter": "qjMakFHDy7sC",
}
# The profile page lists up to 20 papers: the most cited ones, or the newest ones with "sortby=pubdate".
# Longer lists need "cstart" in the address, which Scholar's robots.txt does not allow.
MOST_CITED = f"https://scholar.google.com/citations?user={USER}&hl=en"
NEWEST = MOST_CITED + "&sortby=pubdate"
HEADERS = {
    "User-Agent": "citation-count-updater/1.0 (automated script; reads one public profile page a day)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip",
}
ROW = '<tr class="gsc_a_tr">'
STALE_DAYS = 30


class Refused(Exception):
    """Scholar answered with an error or a robot check instead of the profile, or not at all."""


def fetch(url):
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
    except urllib.error.HTTPError as error:
        raise Refused(f"HTTP {error.code}") from error
    except (OSError, EOFError, zlib.error, http.client.HTTPException) as error:
        raise Refused(str(error) or type(error).__name__) from error
    page = body.decode("utf-8", "replace")
    if ROW not in page:
        title = re.search(r"<title[^>]*>(.*?)</title>", page, re.DOTALL | re.IGNORECASE)
        title = " ".join(title.group(1).split())[:80] if title else "no title"
        raise Refused(f'the page "{title}" has no publication rows, probably a robot check')
    return page


def cited_by(page):
    """Map each paper id on a profile page to its "Cited by" count."""
    found = {}
    for row in page.split(ROW)[1:]:
        paper = re.search(r'citation_for_view=[^"&]*:([\w-]+)', row)
        count = re.search(r'class="gsc_a_ac[^"]*">(\d*)<', row)
        if paper and count:
            found[paper.group(1)] = int(count.group(1) or 0)
    return found


def read_counts():
    """The "Cited by" count of each paper in PAPERS; None for a paper that the profile does not show."""
    found = cited_by(fetch(MOST_CITED))
    if any(paper not in found for paper in PAPERS.values()):
        found = {**cited_by(fetch(NEWEST)), **found}
    return {key: found.get(paper) for key, paper in PAPERS.items()}


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: update_citations.py <citations.json>")
    target = sys.argv[1]
    today = datetime.datetime.now(datetime.timezone.utc).date()
    try:
        with open(target, encoding="utf-8") as file:
            previous = json.load(file)
    except FileNotFoundError:
        previous = {}

    try:
        counts = read_counts()
    except Refused as problem:
        last_read = previous.get("checked") or previous.get("updated")
        days = (today - datetime.date.fromisoformat(last_read)).days if last_read else 0
        if days > STALE_DAYS:
            print(f"::error::Google Scholar has not answered for {days} days ({problem}). "
                  "The citation counts on the site may be out of date.")
            return 1
        print(f"::notice::Google Scholar turned this machine away ({problem}). "
              "The citation counts stay as they are; the next run asks again.")
        return 0

    for key, count in counts.items():
        if count is None:
            print(f"::error::Paper '{key}' ({PAPERS[key]}) is not on the Scholar profile page any more.")
            return 1
        if count == 0 and previous.get(key, 0) > 0:
            print(f"::error::Paper '{key}' dropped from {previous[key]} citations to 0; not writing that.")
            return 1

    changed = any(previous.get(key) != count for key, count in counts.items())
    # "updated" is the day the counts last changed, "checked" the day they were last read.
    updated = today.isoformat() if changed else previous.get("updated", today.isoformat())
    with open(target, "w", encoding="utf-8") as file:
        json.dump({**counts, "updated": updated, "checked": today.isoformat()}, file, indent=2)
        file.write("\n")
    print("Updated:" if changed else "No change:", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
