# Citation counts

`citations.json` holds the Google Scholar "Cited by" counts shown on the citation badges of
<https://www.yichenggu.com/researcher>.

It is refreshed once a day by the workflow `.github/workflows/scholar-citations.yml` on the `main` branch,
which runs `.github/scripts/update_citations.py`. Please don't edit it by hand.
