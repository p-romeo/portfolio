# AGENTS.md — paulromeo.net portfolio

Instructions for AI agents working in this repo.

## What this is
Static portfolio: `build.py` (stdlib-only Python) renders `content/*.md` into `site/`. GitHub Pages deploys on push to main. Live at https://paulromeo.net.

## Rules
1. **Edit content, not code.** Section text lives in `content/`; project cards in `content/projects/*.md` (front matter: title, tag, link, site, weight, hidden). Only touch `build.py` for layout/engine changes.
2. **Verify claims before writing them.** Cert dates/IDs, repo existence (`gh repo view`), live-site URLs (`curl` status), release versions. Paul self-audits; a sourced number or nothing.
3. **Deploy = push to main** (GitHub Actions builds). After push, verify https://paulromeo.net/ and https://paulromeo.net/projects/ return 200 and spot-check the changed content is served.
4. **Never commit secrets.** No keys anywhere in this repo.
5. **Code style: ponytail (full).** Minimal change that works — stdlib before dependencies, shortest diff, no speculative abstraction. `build.py` stays stdlib-only by design; do not add packages.
6. **Don't break:** the fixed-width `.xp-logo` layout invariant, mobile nav wrap at ≤720px, the interaction layer's `prefers-reduced-motion` respect, and the `llms.txt`/`sitemap.xml` generation (they must reflect actual pages).

## Skills to load before working here
- `ponytail` — minimal-code ruleset, mode **full**. Every code task.
- `portfolio-site-ops` — architecture, logo gotchas (WebP-with-.png-extension), layout invariants.
