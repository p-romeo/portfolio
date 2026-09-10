"""Focus-visible QA: tab to a link, screenshot focused state, check outline renders."""
import asyncio, sys
from playwright.async_api import async_playwright

async def main(out_path, url):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1280, "height": 800})
        await pg.goto(url, wait_until="domcontentloaded")
        # Tab until focus lands on a real link
        for _ in range(5):
            await pg.keyboard.press("Tab")
            tag = await pg.evaluate("document.activeElement.tagName")
            if tag == "A":
                break
        info = await pg.evaluate("""(() => {
          const el = document.activeElement;
          const s = getComputedStyle(el);
          return {tag: el.tagName, text: (el.textContent||'').trim().slice(0,30),
                  outline: s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor,
                  visible: el.getBoundingClientRect().top >= 0};
        })()""")
        print("focused:", info)
        await pg.screenshot(path=out_path)
        await b.close()
        assert "solid" in info["outline"], "no outline applied"
        print("PASS: focus outline visible on tab")

asyncio.run(main(sys.argv[1], sys.argv[2]))
