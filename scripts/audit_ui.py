"""Browser regression checks. Run against a locally served build.
Requires Playwright for QA only; the site generator remains stdlib-only.
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

base = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
out = Path(sys.argv[2] if len(sys.argv) > 2 else '/opt/data/portfolio-audit/union-alpha')
out.mkdir(parents=True, exist_ok=True)
results = []

def check(name, ok, detail=None):
    results.append(dict(name=name, passed=bool(ok), detail=detail))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    for route in ['/', '/projects/']:
        slug = 'home' if route == '/' else 'projects'
        for width in [320, 390, 768, 1440]:
            page = browser.new_page(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.goto(base + route, wait_until='networkidle')
            sizes = page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})')
            check(f'{slug} {width}px reflow', sizes['document'] <= width, sizes)
            check(f'{slug} {width}px main landmark', page.locator('main').count() == 1)
            check(f'{slug} {width}px h1', page.locator('h1').count() == 1)
            check(f'{slug} {width}px images', page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.hasAttribute("alt"))'))
            page.keyboard.press('Tab')
            focus = page.evaluate('({tag:document.activeElement.tagName,style:getComputedStyle(document.activeElement).outlineStyle})')
            check(f'{slug} {width}px keyboard focus', focus['tag'] == 'A' and focus['style'] != 'none', focus)
            check(f'{slug} {width}px console', not errors, errors)
            page.screenshot(path=str(out / f'{slug}-{width}.png'), full_page=True)
            page.close()
        page = browser.new_page(java_script_enabled=False, viewport={'width': 390, 'height': 844})
        page.goto(base + route)
        hidden = page.locator('[data-reveal]').evaluate_all('(els)=>els.filter(e=>getComputedStyle(e).opacity==="0").length')
        check(f'{slug} no-JavaScript content', hidden == 0, {'hidden': hidden})
        page.close()
    browser.close()
(out / 'ui-results.json').write_text(json.dumps(results, indent=2))
for r in results:
    if not r['passed']:
        print('FAIL:', r['name'], r['detail'])
print(f'{sum(r["passed"] for r in results)}/{len(results)} checks passed')
sys.exit(any(not r['passed'] for r in results))
