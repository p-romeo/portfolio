"""Interaction regression checks against a locally served build (Playwright QA only)."""
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
    browser = p.chromium.launch(args=['--no-sandbox'])
    for route in ['/', '/projects/']:
        for reduced in ['reduce', 'no-preference']:
            page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion=reduced)
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(base + route)
            for y in range(0, page.evaluate('document.body.scrollHeight'), 500):
                page.evaluate('(y)=>scrollTo(0,y)', y)
                page.wait_for_timeout(100)
            page.wait_for_timeout(1300)
            check(f'{route} {reduced} scroll reveals', page.locator('[data-reveal]').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).opacity==="1")'))
            for selector in (['.badge', '.xp'] if route == '/' else ['.project.featured']):
                card = page.locator(selector).first
                card.scroll_into_view_if_needed()
                page.wait_for_timeout(700)
                box = card.bounding_box()
                page.mouse.move(box['x'] + box['width'] * .8, box['y'] + box['height'] * .6)
                page.wait_for_timeout(500)
                transform = card.evaluate('(e)=>({inline:e.style.transform,computed:getComputedStyle(e).transform})')
                check(f'{selector} {reduced} hover', bool(transform['inline']) if reduced == 'no-preference' else transform['computed'] == 'none', transform)
                page.mouse.move(0, 0)
                page.wait_for_timeout(1200)
                clean = card.evaluate('(e)=>!e.style.transform&&!e.style.backgroundImage&&!e.style.boxShadow')
                check(f'{selector} {reduced} leave cleanup', clean)
            check(f'{route} {reduced} console', not errors, errors)
            page.close()
    page = browser.new_page(viewport={'width':390,'height':844}, reduced_motion='reduce')
    page.goto(base + '/')
    page.locator('nav a[href="/#skills"]').click()
    page.wait_for_timeout(100)
    bounds = page.evaluate('({section:document.querySelector("#skills").getBoundingClientRect().top,header:document.querySelector("header").getBoundingClientRect().bottom})')
    check('mobile anchor clears sticky header', bounds['section'] >= bounds['header'] - 1, bounds)
    page.goto(base + '/')
    targets = page.locator('a').count()
    bad_focus = []
    for _ in range(targets):
        page.keyboard.press('Tab')
        state = page.evaluate('({tag:document.activeElement.tagName,outline:getComputedStyle(document.activeElement).outlineStyle})')
        if state['tag'] != 'A' or state['outline'] == 'none':
            bad_focus.append(state)
    check('all homepage links keyboard reachable with focus', not bad_focus, bad_focus)
    browser.close()
(out / 'interaction-results.json').write_text(json.dumps(results, indent=2))
for r in results:
    if not r['passed']: print('FAIL:', r['name'], r['detail'])
print(f'{sum(r["passed"] for r in results)}/{len(results)} checks passed')
sys.exit(any(not r['passed'] for r in results))
