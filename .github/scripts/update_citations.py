#!/usr/bin/env python3
"""Refresh the citation counts shown on the Researcher page.

Reads the Google Scholar profile once, picks out the papers listed in PAPERS and writes their
"Cited by" counts to a JSON file. The citation badges on the Researcher page read that file.

Usage: update_citations.py <citations.json> [saved-profile.html]
The optional second argument reads a saved copy of the profile page instead of fetching it.
"""
import datetime
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.request

USER = "REtoPf8AAAAJ"
# JSON key -> the paper's id on the Scholar profile (what follows "citation_for_view=USER:" in its link).
PAPERS = {
    "amphion": "d1gkVwhDpl0C",
    "yue2": "YOwf2qJgpHMC",
    "foleycrafter": "qjMakFHDy7sC",
}
URL = f"https://scholar.google.com/citations?user={USER}&hl=en&cstart=0&pagesize=100"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip",
}
ROW = '<tr class="gsc_a_tr">'


class Blocked(Exception):
    """Scholar answered with an error or a robot check instead of the profile."""


def fetch():
    request = urllib.request.Request(URL, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
    except urllib.error.HTTPError as error:
        raise Blocked(f"HTTP {error.code}") from error
    except OSError as error:
        raise Blocked(str(error)) from error
    page = body.decode("utf-8", "replace")
    if ROW not in page:
        raise Blocked("the page has no publication rows (probably a robot check)")
    return page


def fetch_with_retries(waits=(30, 90)):
    for wait in (*waits, None):
        try:
            return fetch()
        except Blocked as problem:
            if wait is None:
                raise
            print(f"Scholar did not answer ({problem}); trying again in {wait}s.")
            time.sleep(wait)


def cited_by(page):
    """Map each paper id on the profile to its "Cited by" count."""
    found = {}
    for row in page.split(ROW)[1:]:
        paper = re.search(r'citation_for_view=[^"&]*:([\w-]+)', row)
        count = re.search(r'class="gsc_a_ac[^"]*">(\d*)<', row)
        if paper and count:
            found[paper.group(1)] = int(count.group(1) or 0)
    return found


def main():
    target = sys.argv[1]
    try:
        with open(target, encoding="utf-8") as file:
            previous = json.load(file)
    except FileNotFoundError:
        previous = {}

    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as file:
            page = file.read()
    else:
        try:
            page = fetch_with_retries()
        except Blocked as problem:
            # Scholar sometimes refuses automated requests. Keep the numbers we have and try again tomorrow.
            print(f"::warning::Google Scholar did not answer ({problem}); the citation counts were left as they are.")
            return 0

    found = cited_by(page)
    counts = {}
    for key, paper in PAPERS.items():
        if paper not in found:
            print(f"::error::Paper '{key}' ({paper}) is not on the Scholar profile page any more.")
            return 1
        if found[paper] == 0 and previous.get(key, 0) > 0:
            print(f"::error::Paper '{key}' dropped from {previous[key]} citations to 0; not writing that.")
            return 1
        counts[key] = found[paper]

    if all(previous.get(key) == value for key, value in counts.items()):
        print("No change:", counts)
        return 0

    counts["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    with open(target, "w", encoding="utf-8") as file:
        json.dump(counts, file, indent=2)
        file.write("\n")
    print("Updated:", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
