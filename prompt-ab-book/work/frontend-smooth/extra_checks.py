"""Extra checks on the edited copy: cache revalidation on reload, mode switch, reduced motion, deep TOC click."""
import json
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8766/"; ORIG = "http://127.0.0.1:8767/"
with sync_playwright() as p:
    b = p.chromium.launch()
    for url in (ORIG, URL):
        c = b.new_context(viewport={"width": 1280, "height": 800}); pg = c.new_page()
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(url); pg.wait_for_timeout(2000)
        statuses = []
        pg.on("response", lambda r: statuses.append(r.status) if "/chapters/" in r.url else None)
        pg.reload(); pg.wait_for_timeout(2000)
        out = {"url": url, "reloadChapterStatuses": sorted(set(statuses)), "n": len(statuses)}
        # mode switch desktop -> phone -> desktop keeps the page
        pg.evaluate("turnTo(leafFor(chapters[4].start))"); pg.wait_for_timeout(2500)
        w1 = pg.evaluate("document.getElementById('where').textContent")
        pg.set_viewport_size({"width": 400, "height": 800}); pg.wait_for_timeout(600)
        w2 = pg.evaluate("document.getElementById('where').textContent")
        pg.set_viewport_size({"width": 1280, "height": 800}); pg.wait_for_timeout(600)
        w3 = pg.evaluate("document.getElementById('where').textContent")
        out["modeSwitch"] = [w1, w2, w3]
        out["nodesAfterModeSwitch"] = pg.evaluate("document.querySelectorAll('*').length")
        # images on the visible spread are loaded (complete) when shown
        pg.evaluate("turnTo(leafFor(chapters[0].start)+1)"); pg.wait_for_timeout(1500)
        out["imgs"] = pg.evaluate("[...document.querySelectorAll('.leaf img')].map(i=>i.getAttribute('src')+':'+(i.complete&&i.naturalWidth>0))")
        out["errors"] = errs
        print(json.dumps(out)); c.close()
    # reduced motion: turns still work, no transition
    c = b.new_context(viewport={"width": 1280, "height": 800}, reduced_motion="reduce"); pg = c.new_page(); pg.goto(URL); pg.wait_for_timeout(2000)
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(100)
    print("reduced-motion", pg.evaluate("[document.getElementById('where').textContent, getComputedStyle(document.querySelector('.leaf')).transitionDuration]"))
    # click on right page turns forward, left page goes back; TOC button click
    pg.mouse.click(1000, 400); pg.wait_for_timeout(100); a = pg.evaluate("document.getElementById('where').textContent")
    pg.mouse.click(300, 400); pg.wait_for_timeout(100); bk = pg.evaluate("document.getElementById('where').textContent")
    print("click right ->", a, "| click left ->", bk)
    c.close(); b.close()
