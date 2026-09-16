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

Keep `Paul-Romeo-Resume.pdf` in the repository root and the Word source at
`tools/Paul-Romeo-Resume.docx`. The build copies both into `site/`; never edit
generated output. Missing downloads fail the build.

## Checks

```bash
python3 -B test_build.py
python3 -B tools/test_resume.py
python3 -B build.py
python3 -B scripts/audit_static.py
```

Browser QA requires Playwright (QA only, not a build dependency). Serve `site/`
locally, then run `scripts/audit_ui.py` and `scripts/audit_interactions.py` with
the Python environment containing Playwright. Both accept a base URL and an
output directory as positional arguments and exit nonzero on failed checks.
