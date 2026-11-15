#!/usr/bin/env python3
"""Skyline card: turns a year of GitHub contributions into a Kuala Lumpur skyline.

1 contribution in the last 365 days = 1 metre of tower. The card compares the total with
four real landmarks and draws the last 26 weeks as buildings (taller week = taller building).

Data sources, first one that works:
  1. SKYLINE_DATA=path.json   a list of [date, count] pairs (used to seed or test)
  2. GITHUB_TOKEN             GraphQL, exact numbers (this is what the Action uses)
  3. no token                 scrape of the public contribution graph

Usage: GH_USERNAME=7YMERA python3 scripts/make_skyline.py     (writes skyline-card.svg and skyline.json at the repo root; the portfolio site reads the JSON)
"""
import json, os, re, sys, urllib.request, html
from datetime import date, datetime, timedelta, timezone

USER = os.environ.get("GH_USERNAME", "7YMERA")
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skyline-card.svg")
LANDMARKS = [("Menara KL", 421.0), ("The Exchange 106", 445.0), ("Petronas Towers", 452.0), ("Merdeka Maybank Tower", 678.9)]
LEVEL_COUNT = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10}  # only used by the scrape fallback when counts are hidden

def http(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def from_graphql():
    q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}", "variables": {"u": USER}}
    raw = http("https://api.github.com/graphql", json.dumps(q).encode(), {"Authorization": "bearer " + TOKEN, "Content-Type": "application/json", "User-Agent": "skyline-card"})
    weeks = json.loads(raw)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [[d["date"], d["contributionCount"]] for w in weeks for d in w["contributionDays"]]

def from_scrape():
    page = http(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "skyline-card"})
    tips = {m.group(1): m.group(2) for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page)}
    out = []
    for m in re.finditer(r'<td[^>]*data-date="([\d-]+)"[^>]*>', page):
        tag = m.group(0); iid = re.search(r'id="([^"]+)"', tag); lvl = re.search(r'data-level="(\d)"', tag)
        n = None
        if iid and iid.group(1) in tips:
            t = re.match(r"(\d+|No) contribution", tips[iid.group(1)])
            if t: n = 0 if t.group(1) == "No" else int(t.group(1))
        if n is None: n = LEVEL_COUNT.get(int(lvl.group(1)) if lvl else 0, 0)
        out.append([m.group(1), n])
    if not out: raise RuntimeError("no contribution cells found")
    return sorted(out)

def load():
    p = os.environ.get("SKYLINE_DATA")
    if p: return json.load(open(p))
    if TOKEN:
        try: return from_graphql()
        except Exception as e: print("graphql failed:", e, file=sys.stderr)
    return from_scrape()

def esc(s): return html.escape(str(s), quote=True)

def build(days):
    days = sorted(days); today = date.fromisoformat(days[-1][0])
    last365 = [(date.fromisoformat(d), c) for d, c in days if date.fromisoformat(d) > today - timedelta(days=365)]
    total = sum(c for _, c in last365)
    # weekly totals for the last 26 weeks, newest last, weeks start Sunday like GitHub
    start = today - timedelta(days=(today.weekday() + 1) % 7)  # this week's Sunday
    weeks = []
    for k in range(25, -1, -1):
        s = start - timedelta(weeks=k); weeks.append(sum(c for d, c in last365 if s <= d < s + timedelta(days=7)))
    active = sum(1 for k in range(52) if sum(c for d, c in last365 if start - timedelta(weeks=k) <= d < start - timedelta(weeks=k) + timedelta(days=7)) > 0)
    best = max((c for _, c in last365), default=0)
    streak = 0; seen = {d: c for d, c in last365}; d = today
    if seen.get(d, 0) == 0: d -= timedelta(days=1)  # today may not have happened yet
    while seen.get(d, 0) > 0: streak += 1; d -= timedelta(days=1)
    metres = float(total)
    passed = [n for n, h in LANDMARKS if metres >= h]
    nxt = next(((n, h) for n, h in LANDMARKS if metres < h), None)
    if nxt: line2 = f"Next: {nxt[0]} at {nxt[1]:g} m, {nxt[1] - metres:.0f} m to go"; prog = metres / nxt[1]
    else: line2 = "Taller than every tower in Kuala Lumpur"; prog = 1.0
    line1 = f"Past {passed[-1]}" if passed else "Still on the ground floor"
    build.stats = {"updated": today.isoformat(), "metres": total, "line1": line1, "line2": line2, "progress": round(prog, 3),
                   "streak": streak, "active_weeks": active, "best_day": best, "weeks": weeks}
    # buildings
    W, H, base = 1000, 340, 292
    mx = max(weeks) or 1; bw, gap, x0 = 13, 3, 570
    bld, win = [], []
    for i, v in enumerate(weeks):
        h = 14 + (v / mx) * 190 if v else 8
        x = x0 + i * (bw + gap); y = base - h; cur = i == len(weeks) - 1
        fill = "#ffd36b" if cur else "url(#tw)"
        bld.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="2" fill="{fill}" opacity="{1 if v else .35}"/>')
        if v:
            rows = int((h - 8) // 12)
            for r in range(rows):
                for c in (0, 1):
                    lit = ((i * 7 + r * 3 + c * 5) % 4) != 0
                    if lit: win.append(f'<rect x="{x + 3 + c * 5}" y="{y + 6 + r * 12:.1f}" width="3" height="4" fill="#061330" opacity=".55"/>')
    pct = max(0.02, min(1, prog)); barw = 440
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(f'{total} contributions in the last year, a tower of {total} metres. {line1}. {line2}.')}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#050f26"/><stop offset="1" stop-color="#0d2e6e"/></linearGradient>
<linearGradient id="tw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fc2ff"/><stop offset="1" stop-color="#2f5fd0"/></linearGradient>
<pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".05"/></pattern></defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="18" fill="url(#g)"/>
<g font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" fill="#fff">
<text x="40" y="52" font-family="Menlo,Consolas,'Courier New',monospace" font-size="14" letter-spacing="3" fill="#ffd36b">SKYLINE LOG</text>
<text x="40" y="128" font-size="76" font-weight="800" letter-spacing="-2">{total:,} m</text>
<text x="40" y="160" font-size="18" fill-opacity=".78">contributions in the last 365 days. 1 contribution = 1 metre.</text>
<text x="40" y="208" font-size="22" font-weight="600">{esc(line1)}</text>
<text x="40" y="236" font-size="17" fill-opacity=".78">{esc(line2)}</text>
<rect x="40" y="252" width="{barw}" height="10" rx="5" fill="#fff" fill-opacity=".14"/><rect x="40" y="252" width="{barw * pct:.0f}" height="10" rx="5" fill="#ffd36b"/>
<g font-family="Menlo,Consolas,'Courier New',monospace" font-size="14" fill-opacity=".85"><text x="40" y="304">STREAK {streak}D</text><text x="190" y="304">ACTIVE WEEKS {active}/52</text><text x="400" y="304">BEST DAY {best}</text></g>
</g>
<g>{''.join(bld)}</g><g>{''.join(win)}</g>
<rect x="{x0 - 10}" y="{base}" width="{26 * (bw + gap) + 14}" height="3" fill="#7fb0ff" fill-opacity=".6"/>
<text x="{x0 - 10}" y="{base + 28}" font-family="Menlo,Consolas,monospace" font-size="12" fill="#fff" fill-opacity=".6">LAST 26 WEEKS, ONE BUILDING EACH</text>
<text x="{W - 40}" y="{base + 28}" text-anchor="end" font-family="Menlo,Consolas,monospace" font-size="12" fill="#fff" fill-opacity=".6">UPDATED {today.isoformat()}</text>
</svg>'''
    return svg

if __name__ == "__main__":
    svg = build(load())
    open(OUT, "w", encoding="utf-8").write(svg); print("wrote", os.path.normpath(OUT))
    jp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skyline.json")
    open(jp, "w", encoding="utf-8").write(json.dumps(build.stats, separators=(",", ":"))); print("wrote", os.path.normpath(jp))
