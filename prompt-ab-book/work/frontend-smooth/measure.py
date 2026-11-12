"""Headless before/after measurement of the page-turning book.

Usage: python3 measure.py   (needs the two servers running:
  original on http://127.0.0.1:8767, edited copy on http://127.0.0.1:8766)

Measures per version and viewport: load-to-render time, DOM nodes, leaves in DOM,
compositor layer count (CDP LayerTree), frame gaps during page turns (rAF),
a z-order check during animations (is the leaf drawn on top the one that is
physically on top?), console errors, horizontal overflow, and takes screenshots.
Headless Chromium composites in software, so frame numbers are a proxy, not GPU truth.
"""
import json, sys, time, pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
URLS = {"before": "http://127.0.0.1:8767/", "after": "http://127.0.0.1:8766/"}
VIEWPORTS = {"desktop": (1280, 800), "phone": (400, 800)}

FRAME_JS = """
async ([action, ms]) => {
  const sleep = t => new Promise(r => setTimeout(r, t));
  const angle = L => { const m = new DOMMatrix(getComputedStyle(L).transform); return Math.abs(Math.atan2(-m.m13, m.m11) * 180 / Math.PI); };
  const gaps = []; let last = performance.now(), run = true, viol = 0, samples = 0, maxLayersInFlight = 0;
  const single = document.getElementById('book').classList.contains('single');
  const loop = t => {
    gaps.push(t - last); last = t;
    // z-order check: among leaves on each side, the one with highest z must be the physically top one.
    // right side: the flying leaf (largest angle < 90) else lowest index; left: flying leaf (smallest angle >= 90) else highest index.
    if (!single) {
      const ls = [...document.querySelectorAll('.leaf')].map((L, k) => ({ i: +(L.dataset.i ?? [...L.parentNode.children].indexOf(L)), z: +L.style.zIndex, a: angle(L) }));
      const R = ls.filter(l => l.a < 90), Lf = ls.filter(l => l.a >= 90);
      const top = a => a.reduce((x, y) => y.z > x.z ? y : x);
      const physR = a => { const mv = a.filter(l => l.a > 0.5); return mv.length ? mv.reduce((x, y) => y.a > x.a ? y : x) : a.reduce((x, y) => y.i < x.i ? y : x); };
      const physL = a => { const mv = a.filter(l => l.a < 179.5); return mv.length ? mv.reduce((x, y) => y.a < x.a ? y : x) : a.reduce((x, y) => y.i > x.i ? y : x); };
      samples++;
      if (R.length && top(R).i !== physR(R).i) viol++;
      if (Lf.length && top(Lf).i !== physL(Lf).i) viol++;
      maxLayersInFlight = Math.max(maxLayersInFlight, ls.filter(l => l.a > 0.5 && l.a < 179.5).length);
    }
    if (run) requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
  await sleep(50);
  ({
    next: () => document.getElementById('next').click(),
    prev: () => document.getElementById('prev').click(),
    rapid: () => { const b = document.getElementById('next'); b.click(); setTimeout(() => b.click(), 150); setTimeout(() => b.click(), 300); },
    reverse: () => { document.getElementById('next').click(); setTimeout(() => document.getElementById('prev').click(), 600); },
    toc: () => document.querySelector(`[data-go="${chapters[2].start}"]`).click(),   // contents -> chapter 3 (button on the visible contents page)
    far: () => turnTo(leafFor(chapters[15].start)),                                    // chapter 3 -> chapter 16 (what a contents click on the last entry does)
  })[action]();
  await sleep(ms);
  run = false;
  gaps.shift();
  const s = [...gaps].sort((a, b) => b - a);
  return { frames: gaps.length, maxGapMs: +s[0].toFixed(1), over33ms: gaps.filter(g => g > 33.4).length,
           p95: +s[Math.floor(s.length * 0.05)].toFixed(1), zViolations: viol, zSamples: samples, maxLeavesMoving: maxLayersInFlight,
           where: document.getElementById('where').textContent };
}
"""

def layers(cdp):
    got = {}
    def on(e): got["n"] = len(e.get("layers") or [])
    cdp.on("LayerTree.layerTreeDidChange", on)
    cdp.send("LayerTree.enable")
    time.sleep(0.6)
    cdp.send("LayerTree.disable")
    return got.get("n")

def run(version, url, vp, browser):
    w, h = VIEWPORTS[vp]
    ctx = browser.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    t0 = time.time()
    page.goto(url)
    page.wait_for_selector(".leaf .paper, .leaf .cover", state="attached", timeout=15000)
    render_ms = round((time.time() - t0) * 1000)
    page.wait_for_timeout(1500)
    cdp = ctx.new_cdp_session(page)
    r = {"version": version, "viewport": vp, "renderMs": render_ms,
         "compat": page.evaluate("document.compatMode"),
         "nodes": page.evaluate("document.querySelectorAll('*').length"),
         "leavesInDom": page.evaluate("document.querySelectorAll('.leaf').length")}
    page.screenshot(path=str(OUT / f"{version}-{vp}-cover.png"))
    r["turn_open_cover"] = page.evaluate(FRAME_JS, ["next", 1500])
    page.screenshot(path=str(OUT / f"{version}-{vp}-p1.png"))
    r["turn_next"] = page.evaluate(FRAME_JS, ["next", 1500])
    r["turn_rapid3"] = page.evaluate(FRAME_JS, ["rapid", 1900])
    r["turn_reverse_midflight"] = page.evaluate(FRAME_JS, ["reverse", 1900])
    # back to contents, click the chapter 3 entry, then a long jump to chapter 16
    page.evaluate("turnTo(leafFor(1))"); page.wait_for_timeout(3000)
    r["toc_click_ch3"] = page.evaluate(FRAME_JS, ["toc", 3500 if version == "after" else 5000])
    r["far_jump_ch16"] = page.evaluate(FRAME_JS, ["far", 3000 if version == "after" else 30000])
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / f"{version}-{vp}-jumped.png"))
    r["nodesAfterJump"] = page.evaluate("document.querySelectorAll('*').length")
    r["turn_prev"] = page.evaluate(FRAME_JS, ["prev", 1500])
    # overflow: page-level horizontal scroll, and whether the open page body needs scrolling
    r["hScroll"] = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    r["savedPage"] = page.evaluate("localStorage.getItem('prompt-book-page')")
    # reload restores saved page?
    page.reload(); page.wait_for_selector(".leaf .paper", state="attached", timeout=15000); page.wait_for_timeout(1200)
    r["whereAfterReload"] = page.evaluate("document.getElementById('where').textContent")
    # resize cost (container-query relayout of every mounted face)
    r["resizeRelayoutMs"] = page.evaluate("""() => { const b=document.getElementById('book'); const t=performance.now(); b.style.width='700px'; document.body.offsetHeight; const d=performance.now()-t; b.style.width=''; document.body.offsetHeight; return +d.toFixed(1); }""")
    # keyboard
    before = page.evaluate("document.getElementById('where').textContent")
    page.keyboard.press("ArrowRight"); page.wait_for_timeout(1300)
    r["keyboardTurns"] = before != page.evaluate("document.getElementById('where').textContent")
    r["consoleErrors"] = errors
    ctx.close()
    return r

def overflow_scan(url, vp, browser):
    """Turn through the whole book one spread at a time (no animation) and list pages whose body overflows."""
    w, h = VIEWPORTS[vp]
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page(); page.goto(url); page.wait_for_selector(".leaf .paper", state="attached", timeout=15000); page.wait_for_timeout(1500)
    res = page.evaluate("""async () => {
      const over = [];
      const n = (typeof nLeaves !== 'undefined') ? nLeaves : leaves.length;
      for (let i = 0; i <= n; i++) {
        turnTo(i); await new Promise(r => setTimeout(r, 30));
        for (const p of visiblePages()) {
          const leaf = narrowMatches() ? p : (p % 2 === 0 ? p / 2 : (p - 1) / 2);
          const el = [...document.querySelectorAll('.leaf')].find((L, k) => (L.dataset.i !== undefined ? +L.dataset.i : k) === leaf);
          if (!el) { over.push('missing leaf ' + leaf); continue; }
          const face = el.querySelector(narrowMatches() || p % 2 === 0 ? '.front' : '.back');
          const b = face.querySelector('.body');
          if (b && b.scrollHeight > b.clientHeight + 2) over.push(p);
        }
      }
      return over;
    }""")
    ctx.close()
    return res

if __name__ == "__main__":
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp in VIEWPORTS:
            for version, url in URLS.items():
                r = run(version, url, vp, browser)
                r["overflowingPages"] = overflow_scan(url, vp, browser)
                results.append(r)
                print(json.dumps(r), flush=True)
        browser.close()
    (OUT / "results.json").write_text(json.dumps(results, indent=1))
