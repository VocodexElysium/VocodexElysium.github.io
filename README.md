# Yicheng Gu's Personal Website

[https://www.yichenggu.com/](https://www.yichenggu.com/)

| Page | File | Contents |
| --- | --- | --- |
| Main | `index.html` | Profile, about me, milestones, education |
| Researcher | `researcher.html` | Publications, projects, experience, services |
| Artist | `artist.html` | Coming soon |

All pages share `style.css` and `site.js`. The design is based on [Jon Barron's template](https://jonbarron.info/).

The citation counts on the Researcher page refresh by themselves: once a day the workflow in
`.github/workflows/scholar-citations.yml` asks Google Scholar for them and stores them in `citations.json` on the
`scholar-stats` branch, which the citation badges display. Scholar does not answer GitHub's machines every day, so
the counts can be a few days behind.
