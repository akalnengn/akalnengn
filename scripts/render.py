"""Render the space-themed SVG assets for the GitHub profile README.

Static assets (banner, toolkit) are rendered from this file.
Live cards (stats, languages) are rendered from data/stats.json,
which scripts/fetch_stats.py refreshes daily via GitHub Actions.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BG_TOP = "#060914"
BG_BOTTOM = "#0e1530"
BORDER = "#1f2a4d"
ACCENT = "#7aa2ff"
WARM = "#ffb86b"
TEXT = "#e6edf3"
MUTED = "#8b98b8"
MONO = '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace'
SANS = '"Segoe UI", -apple-system, Helvetica, Arial, sans-serif'

LANG_COLORS = {
    "Dart": "#00B4AB", "Python": "#3572A5", "C#": "#178600", "Java": "#B07219",
    "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "HTML": "#E34C26",
    "CSS": "#663399", "Go": "#00ADD8", "Kotlin": "#A97BFF", "SQL": "#E38C00",
}


def starfield(rng, w, h, count, twinkle_every=6):
    out = []
    for i in range(count):
        x, y = rng.uniform(4, w - 4), rng.uniform(4, h - 4)
        r = rng.choice([0.5, 0.7, 0.9, 1.1, 1.4])
        o = rng.uniform(0.25, 0.9)
        if i % twinkle_every == 0:
            d, delay = rng.uniform(2.5, 6), rng.uniform(0, 5)
            out.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{o:.2f}" '
                f'class="tw" style="animation-duration:{d:.1f}s;animation-delay:{delay:.1f}s"/>'
            )
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{o:.2f}"/>')
    return "".join(out)


def frame_open(w, h, title, extra_style=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">
<title>{title}</title>
<style>
  .tw {{ animation-name: tw; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
  @keyframes tw {{ 0%,100% {{ opacity: .12 }} 50% {{ opacity: 1 }} }}
  .mono {{ font-family: {MONO}; }}
  .sans {{ font-family: {SANS}; }}
  {extra_style}
</style>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/>
  </linearGradient>
  <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="url(#sky)"/>
'''


def frame_close(w, h):
    return f'''</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{BORDER}"/>
</svg>
'''


def banner():
    w, h = 1200, 220
    rng = random.Random(7)
    meteor_css = """
  .m { opacity: 0; animation-name: fly; animation-iteration-count: infinite; animation-timing-function: ease-out; }
  @keyframes fly {
    0% { opacity: 0; transform: translate(0, 0); }
    2% { opacity: 1; }
    9% { opacity: 0; transform: translate(-320px, 150px); }
    100% { opacity: 0; transform: translate(-320px, 150px); }
  }
  .drift { animation: drift 60s linear infinite; }
  @keyframes drift { from { transform: translateX(0); } to { transform: translateX(-40px); } }
"""
    meteors = []
    for (x, y, dur, delay) in [(980, 18, 9, 1.5), (640, -10, 13, 6), (1180, 40, 17, 11)]:
        meteors.append(
            f'<g class="m" style="animation-duration:{dur}s;animation-delay:{delay}s">'
            f'<line x1="{x - 110}" y1="{y + 52}" x2="{x}" y2="{y}" stroke="url(#trail)" stroke-width="1.6" '
            f'stroke-linecap="round"/>'
            f'<circle cx="{x - 110}" cy="{y + 52}" r="1.6" fill="#fff"/></g>'
        )
    svg = frame_open(w, h, "Starfield", meteor_css)
    svg += f'<g class="drift">{starfield(rng, w + 40, h, 170)}</g>'
    svg += "".join(meteors)
    svg += (
        f'<text x="{w - 34}" y="{h - 26}" text-anchor="end" class="mono" font-size="13" '
        f'letter-spacing="2" fill="{MUTED}">backend · automation · rpa → ai agents</text>'
    )
    svg += frame_close(w, h)
    (ASSETS / "banner.svg").write_text(svg)


def chip_row(x, y, label, chips, color, max_w):
    out = [f'<text x="{x}" y="{y}" class="mono" font-size="12" letter-spacing="2.5" fill="{color}">{label}</text>']
    cx, cy = x, y + 16
    for name in chips:
        cw = 24 + 8.4 * len(name)
        if cx + cw > x + max_w:
            cx, cy = x, cy + 42
        out.append(
            f'<rect x="{cx:.1f}" y="{cy}" width="{cw:.1f}" height="30" rx="15" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".45"/>'
            f'<text x="{cx + cw / 2:.1f}" y="{cy + 20}" text-anchor="middle" class="mono" font-size="14" fill="{TEXT}">{name}</text>'
        )
        cx += cw + 10
    return "".join(out), cy + 30


def toolkit():
    w = 900
    rows = [
        ("IN PRODUCTION", ACCENT, [".NET Core", "C#", "ASP.NET Core", "SQL Server", "Entity Framework", "RPA",
                                   "REST APIs", "Clean Architecture", "Docker", "Git", "CI/CD"]),
        ("BUILDING WITH", WARM, ["Python", "LLMs", "AI Agents", "RAG", "LangGraph", "Vector DBs",
                                 "LLM Evals", "MCP", "FastAPI", "Azure AI"]),
        ("ALSO SHIPPED", MUTED, ["Flutter", "Dart", "Java", "Spring Boot", "PostgreSQL", "React", "AWS", "Kubernetes"]),
    ]
    body, y = [], 46
    for label, color, chips in rows:
        part, bottom = chip_row(40, y, label, chips, color, w - 80)
        body.append(part)
        y = bottom + 38
    h = y - 8
    rng = random.Random(11)
    svg = frame_open(w, h, "Toolkit")
    svg += starfield(rng, w, h, 60, twinkle_every=5)
    svg += "".join(body)
    svg += frame_close(w, h)
    (ASSETS / "toolkit.svg").write_text(svg)


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def stats_card(data):
    w, h = 495, 195
    rng = random.Random(3)
    items = [
        ("Stars earned", data["stars"]),
        ("Contributions · last year", data["contributions"]),
        ("Commits · last year", data["commits"]),
        ("Repositories", data["repositories"]),
        ("Followers", data["followers"]),
    ]
    svg = frame_open(w, h, "GitHub stats")
    svg += starfield(rng, w, h, 40, twinkle_every=5)
    svg += f'<text x="26" y="36" class="mono" font-size="12" letter-spacing="2.5" fill="{ACCENT}">TELEMETRY</text>'
    for i, (label, value) in enumerate(items):
        y = 66 + i * 26
        svg += f'<text x="26" y="{y}" class="sans" font-size="14" fill="{MUTED}">{label}</text>'
        svg += f'<text x="{w - 26}" y="{y}" text-anchor="end" class="mono" font-size="15" font-weight="700" fill="{TEXT}">{fmt(value)}</text>'
    svg += frame_close(w, h)
    (ASSETS / "stats.svg").write_text(svg)


def langs_card(data):
    w, h = 495, 195
    rng = random.Random(5)
    langs = data["languages"][:5]
    total = sum(v for _, v in langs) or 1
    svg = frame_open(w, h, "Most used languages")
    svg += starfield(rng, w, h, 40, twinkle_every=5)
    svg += f'<text x="26" y="36" class="mono" font-size="12" letter-spacing="2.5" fill="{ACCENT}">MOST USED LANGUAGES</text>'
    if not langs:
        svg += f'<text x="{w / 2}" y="104" text-anchor="middle" class="sans" font-size="14" fill="{MUTED}">Charted from public missions.</text>'
        svg += f'<text x="{w / 2}" y="128" text-anchor="middle" class="mono" font-size="13" fill="{WARM}">first launch in preparation</text>'
        svg += frame_close(w, h)
        (ASSETS / "langs.svg").write_text(svg)
        return
    x = 26.0
    bar_w = w - 52
    svg += '<clipPath id="bar"><rect x="26" y="52" width="%d" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">' % bar_w
    for name, v in langs:
        seg = bar_w * v / total
        svg += f'<rect x="{x:.1f}" y="52" width="{seg + 0.5:.1f}" height="10" fill="{LANG_COLORS.get(name, ACCENT)}"/>'
        x += seg
    svg += "</g>"
    for i, (name, v) in enumerate(langs):
        col, row = i % 2, i // 2
        lx, ly = 26 + col * 230, 92 + row * 30
        svg += f'<circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{LANG_COLORS.get(name, ACCENT)}"/>'
        svg += f'<text x="{lx + 18}" y="{ly}" class="sans" font-size="14" fill="{TEXT}">{name}</text>'
        svg += f'<text x="{lx + 200}" y="{ly}" text-anchor="end" class="mono" font-size="13" fill="{MUTED}">{100 * v / total:.1f}%</text>'
    svg += frame_close(w, h)
    (ASSETS / "langs.svg").write_text(svg)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "static"):
        banner()
        toolkit()
    if what in ("all", "cards"):
        data = json.loads((ROOT / "data" / "stats.json").read_text())
        stats_card(data)
        langs_card(data)
