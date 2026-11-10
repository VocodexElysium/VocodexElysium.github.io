# Citation counts

`citations.json` holds the Google Scholar "Cited by" counts shown on the citation badges of
<https://www.yichenggu.com/researcher>.

Once a day the workflow `.github/workflows/scholar-citations.yml` on the `main` branch asks Google Scholar for
them, by running `.github/scripts/update_citations.py`. Scholar does not answer GitHub's machines every day, so
the counts can be a few days behind. Please don't edit the file by hand.

`updated` is the day the counts last changed; `checked` is the day they were last read from Google Scholar.
