# Citation counts

`citations.json` holds the Google Scholar "Cited by" counts shown on the citation badges of
<https://www.yichenggu.com/researcher>.

Once a day the workflow `.github/workflows/scholar-citations.yml` on the `main` branch asks Google Scholar for
them, by running `.github/scripts/update_citations.py`. Scholar turns away most of GitHub's machines, so the file
is also refreshed with the same script whenever the website is updated. Please don't type numbers into it.

`updated` is the day the counts last changed; `checked` is the day they were last read from Google Scholar.
