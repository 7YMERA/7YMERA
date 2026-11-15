#!/usr/bin/env python3
"""Toolkit card: edit GROUPS below, run `python3 scripts/make_toolkit.py`, commit toolkit-card.svg."""
import os, html
GROUPS = [
    ("BUILD", ["Next.js", "React", "TypeScript", "Tailwind CSS", "FastAPI", "Python", "Three.js"]),
    ("DATA", ["SQL", "PostgreSQL", "Supabase", "Row-level security", "Power BI", "Excel"]),
    ("ANALYSIS AND AI", ["Requirements", "Functional specs", "Process mapping", "AI use-case discovery", "LLM evaluation", "Claude", "Bedrock"]),
    ("PLATFORMS", ["Power Platform", "Apps Script", "AWS", "Vercel", "GitHub Actions"]),
]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "toolkit-card.svg")
W, PAD, ROW_H, CH = 1000, 40, 44, 34
def chip_w(t): return int(len(t) * 8.6 + 30)
y = 92; parts = []
for g, items in GROUPS:
    parts.append(f'<text x="{PAD}" y="{y}" font-family="Menlo,Consolas,monospace" font-size="13" letter-spacing="3" fill="#ffd36b">{html.escape(g)}</text>')
    y += 16; x = PAD
    for t in items:
        w = chip_w(t)
        if x + w > W - PAD: x = PAD; y += ROW_H
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{CH}" rx="17" fill="#fff" fill-opacity=".07" stroke="#fff" stroke-opacity=".35"/><text x="{x + w / 2}" y="{y + 22}" text-anchor="middle" font-family="\'Segoe UI\',Arial,sans-serif" font-size="15" fill="#fff">{html.escape(t)}</text>')
        x += w + 10
    y += ROW_H + 26
H = y - 6
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Toolkit: {html.escape(', '.join(i for _, its in GROUPS for i in its))}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#050f26"/><stop offset="1" stop-color="#0d2e6e"/></linearGradient>
<pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".05"/></pattern></defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="18" fill="url(#g)"/>
<text x="{PAD}" y="48" font-family="Menlo,Consolas,monospace" font-size="14" letter-spacing="3" fill="#fff" fill-opacity=".7">TOOLKIT</text>
{''.join(parts)}
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg); print("wrote", os.path.normpath(OUT))
