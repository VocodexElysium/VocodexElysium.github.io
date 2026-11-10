# Yicheng Gu's Personal Website

[https://www.yichenggu.com/](https://www.yichenggu.com/)

| Page | File | Contents |
| --- | --- | --- |
| Main | `index.html` | Profile, about me, milestones, education |
| Researcher | `researcher.html` | Publications, projects, experience, services |
| Artist | `artist.html` | Coming soon |

All pages share `style.css` and `site.js`. The design is based on [Jon Barron's template](https://jonbarron.info/).

The citation counts on the Researcher page are kept in `citations.json` on the `scholar-stats` branch, which the
citation badges display. Once a day the workflow in `.github/workflows/scholar-citations.yml` asks Google Scholar for
them. Scholar turns away most of GitHub's machines, so the counts are also refreshed whenever the site is updated: run
`.github/scripts/update_citations.py` on `citations.json` in a checkout of the `scholar-stats` branch, then commit and
push it.
