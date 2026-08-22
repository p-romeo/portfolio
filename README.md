# Portfolio site

Static portfolio for Paul Joseph Romeo — markdown in, polished dark-theme HTML out.

## Edit content, not code

Everything on the site comes from `content/`:

| File | Renders as |
|---|---|
| `content/about.md` | About section |
| `content/certifications.md` | Certification badges (`- **Name** | Issuer | Year`) |
| `content/skills.md` | Skill chips (`## Category` + comma-separated list) |
| `content/projects/*.md` | Project cards (front matter: title, tag, link, weight) |

## Build & deploy

```bash
python3 build.py        # renders site/index.html
git push                # GitHub Pages workflow deploys site/ automatically
```

Drop `Paul-Romeo-Resume.pdf` into `site/` (or update the link in `build.py`) for the résumé download.
