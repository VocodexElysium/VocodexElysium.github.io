#!/usr/bin/env python3
"""Refresh the citation counts shown on the Researcher page.

Reads the Google Scholar profile, picks out the papers listed in PAPERS and writes their "Cited by" counts
to a JSON file. The citation badges on the Researcher page read that file.

Usage: update_citations.py <citations.json> [--again]

The counts are read once a day; --again reads them even if that already happened today.

Google Scholar turns away some of GitHub's machines, so the workflow runs this script several times in a
row, each time on another machine. Being turned away is therefore not an error, unless nothing has got
through for STALE_DAYS days.
"""
import argparse
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
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip",
}
ROW = '<tr class="gsc_a_tr">'
# Without an answer from Scholar for this many days, the run fails, so that GitHub sends a notice.
STALE_DAYS = 14


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
        raise Refused("the page has no publication rows, probably a robot check")
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
    parser = argparse.ArgumentParser(description="Refresh the citation counts shown on the Researcher page.")
    parser.add_argument("target", help="the JSON file that holds the counts")
    parser.add_argument("--again", action="store_true", help="read the counts even if they were already read today")
    options = parser.parse_args()

    today = datetime.datetime.now(datetime.timezone.utc).date()
    try:
        with open(options.target, encoding="utf-8") as file:
            previous = json.load(file)
    except FileNotFoundError:
        previous = {}

    if previous.get("checked") == today.isoformat() and not options.again:
        print("The counts were already read today.")
        return 0

    try:
        counts = read_counts()
    except Refused as problem:
        last_read = previous.get("checked") or previous.get("updated")
        days = (today - datetime.date.fromisoformat(last_read)).days if last_read else 0
        if days > STALE_DAYS:
            print(f"::error::Google Scholar has not answered for {days} days ({problem}). "
                  "The citation counts on the site may be out of date.")
            return 1
        print(f"::notice::Google Scholar turned this machine away ({problem}). The citation counts stay as they are.")
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
    with open(options.target, "w", encoding="utf-8") as file:
        json.dump({**counts, "updated": updated, "checked": today.isoformat()}, file, indent=2)
        file.write("\n")
    print("Updated:" if changed else "No change:", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
