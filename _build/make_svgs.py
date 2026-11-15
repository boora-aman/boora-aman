"""Generate theme-aware SVG cards for the GitHub profile README.

Run: python3 github-profile/_build/make_svgs.py
Writes assets/{hero,stack}-{dark,light}.svg next to README.md.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0a0e13", panel="#0f151d", panel2="#121a24", border="#1f2b38", grid="#16202b",
                 text="#e6edf3", muted="#8293a7", dim="#4b5a6b", accent="#2dd4bf", accent_soft="#2dd4bf22",
                 amber="#f5b84a", glow="#2dd4bf"),
    "light": dict(bg="#f8fafb", panel="#ffffff", panel2="#f1f5f8", border="#dbe3ea", grid="#eef2f5",
                  text="#0d1620", muted="#55657a", dim="#9aa8b8", accent="#0d9488", accent_soft="#0d948818",
                  amber="#b7791f", glow="#14b8a6"),
}

SANS = "Inter, 'Segoe UI', -apple-system, system-ui, Roboto, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', 'SF Mono', Menlo, Consolas, monospace"
CH = 7.6  # approx mono char width at 12.5px


def reveal(delay, dur):
    """Opacity 0 -> 1 after `delay`. Base value stays 1, so the static image is complete without SMIL."""
    total = delay + dur
    k = delay / total
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{total:.2f}s" '
            f'begin="0s" fill="freeze"/>')


def typed_width(delay, dur, full):
    total = delay + dur
    k = delay / total
    return (f'<animate attributeName="width" values="0;0;{full:.0f}" keyTimes="0;{k:.3f};1" dur="{total:.2f}s" '
            f'begin="0s" fill="freeze"/>')


def chip(x, y, label, t, strong=False, size=12, h=24, begin=None):
    w = len(label) * size * 0.6 + 20
    fill = t["accent_soft"] if strong else t["panel2"]
    stroke = t["accent"] if strong else t["border"]
    color = t["accent"] if strong else t["text"]
    anim = reveal(begin, 0.5) if begin is not None else ""
    op = ""
    return w, (f'<g{op}>{anim}<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="6" fill="{fill}" '
               f'stroke="{stroke}" stroke-width="1"/><text x="{x + w / 2:.1f}" y="{y + h / 2 + size * 0.36:.1f}" '
               f'text-anchor="middle" font-family="{MONO}" font-size="{size}" fill="{color}">{escape(label)}</text></g>')


def grid(t, w, h, step=24):
    return (f'<defs><pattern id="g" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<path d="M{step} 0H0V{step}" fill="none" stroke="{t["grid"]}" stroke-width="1"/></pattern>'
            f'<radialGradient id="glow" cx="0.12" cy="0.1" r="0.7"><stop offset="0" stop-color="{t["glow"]}" stop-opacity="0.16"/>'
            f'<stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="fade" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{t["bg"]}" stop-opacity="0.9"/></linearGradient>'
            f'<clipPath id="card"><rect width="{w}" height="{h}" rx="16"/></clipPath></defs>'
            f'<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="{t["bg"]}"/>'
            f'<rect width="{w}" height="{h}" fill="url(#g)"/><rect width="{w}" height="{h}" fill="url(#glow)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#fade)"/></g>'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{t["border"]}"/>')


def hero(t):
    W, H = 1000, 340
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Aman Boora — full-stack product engineer building ERP, CRM, SaaS and AI systems">', grid(t, W, H)]

    # status line with pulsing dot
    p.append(f'<circle cx="54" cy="58" r="4" fill="{t["accent"]}"/>'
             f'<circle cx="54" cy="58" r="4" fill="none" stroke="{t["accent"]}" stroke-width="1.5">'
             f'<animate attributeName="r" values="4;11" dur="2s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0.9;0" dur="2s" repeatCount="indefinite"/></circle>'
             f'<text x="68" y="62" font-family="{MONO}" font-size="12" fill="{t["muted"]}" letter-spacing="0.5">'
             f'ONLINE · DEHRADUN, IN · SHIPPING TO PRODUCTION</text>')
    p.append(f'<text x="48" y="128" font-family="{SANS}" font-size="56" font-weight="800" fill="{t["text"]}" '
             f'letter-spacing="-1.5">Aman Boora<tspan fill="{t["accent"]}">.</tspan></text>')
    p.append(f'<text font-family="{SANS}" font-size="19" fill="{t["muted"]}">'
             f'<tspan x="48" y="170">I build the systems businesses run on —</tspan>'
             f'<tspan x="48" y="196"><tspan fill="{t["text"]}" font-weight="600">ERP, CRM, SaaS</tspan> and the '
             f'<tspan fill="{t["text"]}" font-weight="600">AI</tspan> that drives them.</tspan></text>')
    p.append(f'<text x="48" y="238" font-family="{MONO}" font-size="12.5" fill="{t["accent"]}">'
             f'product engineer · founder @ ABM Tech · Alfastack</text>')
    x = 48
    for i, (lab, strong) in enumerate([("Frappe/ERPNext", True), ("Next.js", False), ("Rust", False),
                                       ("React Native", False), ("LLM agents", True)]):
        w, s = chip(x, 260, lab, t, strong, begin=0.3 + i * 0.12)
        p.append(s)
        x += w + 8

    # terminal
    tx, ty, tw, th = 572, 40, 384, 260
    p.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>'
             f'<path d="M{tx} {ty + 34}H{tx + tw}" stroke="{t["border"]}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        p.append(f'<circle cx="{tx + 20 + i * 16}" cy="{ty + 17}" r="5" fill="{c}" opacity="0.85"/>')
    p.append(f'<text x="{tx + tw / 2}" y="{ty + 21}" text-anchor="middle" font-family="{MONO}" font-size="11.5" '
             f'fill="{t["dim"]}">aman@abm: ~</text>')
    lines = [
        ("$", "whoami", "cmd"),
        ("", "product engineer · erp / crm / saas", "out"),
        ("$", "uptime", "cmd"),
        ("", "3+ yrs shipping · 10+ systems live", "out"),
        ("$", "ls ~/shipping", "cmd"),
        ("", "nestiq  abm-crm  benchpilot  petrodiesel", "acc"),
    ]
    begin, ly = 0.6, ty + 66
    for i, (pr, txt, kind) in enumerate(lines):
        full = (len(txt) + (2 if pr else 2)) * CH + 8
        dur = 0.05 * len(txt) if kind == "cmd" else 0.25
        cid = f"l{i}"
        p.append(f'<clipPath id="{cid}"><rect x="{tx + 18}" y="{ly - 14}" width="{full:.0f}" height="20">'
                 f'{typed_width(begin, dur, full)}</rect></clipPath>')
        color = {"cmd": t["text"], "out": t["muted"], "acc": t["accent"]}[kind]
        prompt = f'<tspan fill="{t["amber"]}">{pr}</tspan> ' if pr else "  "
        p.append(f'<text x="{tx + 18}" y="{ly}" clip-path="url(#{cid})" font-family="{MONO}" font-size="12.5" '
                 f'fill="{color}" xml:space="preserve">{prompt}{escape(txt)}</text>')
        begin += dur + (0.25 if kind == "cmd" else 0.45)
        ly += 28
    p.append(f'<text x="{tx + 18}" y="{ly}" font-family="{MONO}" font-size="12.5" fill="{t["amber"]}">$'
             f'{reveal(begin, 0.01)}</text>'
             f'<rect x="{tx + 18 + 2 * CH}" y="{ly - 12}" width="8" height="15" fill="{t["accent"]}">'
             f'{reveal(begin, 0.01)}'
             f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{begin:.2f}s" '
             f'repeatCount="indefinite"/></rect>')
    # scan line over terminal
    p.append(f'<rect x="{tx + 1}" y="{ty + 35}" width="{tw - 2}" height="2" fill="{t["accent"]}" opacity="0.08">'
             f'<animate attributeName="y" values="{ty + 35};{ty + th - 4};{ty + 35}" dur="6s" repeatCount="indefinite"/></rect>')
    p.append("</svg>")
    return "".join(p)


LAYERS = [
    ("INTELLIGENCE", [("LLM agents", 1), ("Claude", 0), ("Gemini", 0), ("OpenRouter", 0), ("vision models", 0)]),
    ("INTERFACE", [("Next.js", 1), ("React", 0), ("Vue 3", 0), ("Tailwind", 0), ("React Native · Expo", 0), ("Frappe UI", 0)]),
    ("SERVICES", [("Frappe · ERPNext", 1), ("FastAPI", 0), ("Flask", 0), ("Node.js", 0), ("Rust engine", 0), ("Go agent", 0)]),
    ("INTEGRATIONS", [("Meta Graph API", 0), ("WhatsApp", 0), ("3CX PBX", 0), ("Cashfree", 0), ("Razorpay", 0), ("WebSockets", 0)]),
    ("DATA", [("MariaDB", 1), ("PostgreSQL", 0), ("MongoDB", 0), ("Redis", 0), ("Prisma", 0)]),
    ("INFRA", [("Linux", 0), ("Docker", 1), ("Traefik", 0), ("Nginx", 0), ("GitHub Actions", 0), ("Vercel", 0)]),
    ("LANGUAGES", [("Python", 1), ("TypeScript", 1), ("JavaScript", 0), ("Rust", 0), ("Go", 0), ("Kotlin", 0), ("SQL", 0)]),
]


def stack(t):
    W = 1000
    row, top = 46, 78
    H = top + row * len(LAYERS) + 26
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Tech stack, layered from AI to languages">', grid(t, W, H)]
    p.append(f'<text x="48" y="48" font-family="{MONO}" font-size="12" fill="{t["muted"]}" letter-spacing="1">'
             f'<tspan fill="{t["accent"]}">▍</tspan> STACK.YAML — top of the request to bottom of the server</text>')
    count = sum(len(items) for _, items in LAYERS)
    p.append(f'<text x="{W - 48}" y="48" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t["dim"]}">'
             f'{len(LAYERS)} layers · {count} tools · <tspan fill="{t["accent"]}">all used in real work</tspan></text>')
    spine_x = 56
    p.append(f'<path d="M{spine_x} {top + 12}V{top + row * (len(LAYERS) - 1) + 12}" stroke="{t["border"]}" stroke-width="2"/>')
    # travelling packet on the spine
    p.append(f'<circle cx="{spine_x}" cy="{top + 12}" r="3.5" fill="{t["accent"]}"><animate attributeName="cy" '
             f'values="{top + 12};{top + row * (len(LAYERS) - 1) + 12};{top + 12}" dur="7s" repeatCount="indefinite"/></circle>')
    for i, (label, items) in enumerate(LAYERS):
        y = top + i * row
        p.append(f'<circle cx="{spine_x}" cy="{y + 12}" r="5" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="2"/>')
        p.append(f'<text x="{spine_x + 20}" y="{y + 16}" font-family="{MONO}" font-size="11.5" font-weight="700" '
                 f'fill="{t["muted"]}" letter-spacing="1.2">{label}</text>')
        x = 214
        for j, (lab, strong) in enumerate(items):
            w, s = chip(x, y, lab, t, bool(strong), begin=0.15 + i * 0.12 + j * 0.04)
            p.append(s)
            x += w + 8
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    import re, sys
    OUT.mkdir(parents=True, exist_ok=True)
    preview = Path(sys.argv[1]) if len(sys.argv) > 1 else None  # optional dir for animation-free previews
    for name, t in THEMES.items():
        for kind, fn in (("hero", hero), ("stack", stack)):
            svg = fn(t)
            (OUT / f"{kind}-{name}.svg").write_text(svg)
            if preview:
                preview.mkdir(parents=True, exist_ok=True)
                (preview / f"{kind}-{name}.svg").write_text(re.sub(r"<animate [^>]*/>", "", svg))
    print("written to", OUT)
