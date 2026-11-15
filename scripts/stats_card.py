"""Render a GitHub stats card (SVG) for the profile README.

Runs in GitHub Actions (see .github/workflows/profile-cards.yml) with GITHUB_TOKEN,
so it never depends on a third-party stats server being up.

Usage: python3 scripts/stats_card.py <login> <out.svg>
"""
import json
import os
import sys
import urllib.request
from html import escape

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar { totalContributions }
    }
  }
}
"""

C = dict(bg="#1a1b27", border="#2a2e45", title="#70a5fd", text="#c0caf5", value="#38bdae", icon="#bf91f3",
         muted="#565f89", bar_bg="#24283b")
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"


def fetch(login: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def fmt(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def render(u: dict) -> str:
    cc = u["contributionsCollection"]
    repos = u["repositories"]
    stars = sum(r["stargazerCount"] for r in repos["nodes"])
    langs: dict[str, list] = {}
    for r in repos["nodes"]:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            entry = langs.setdefault(name, [0, e["node"]["color"] or "#888"])
            entry[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    total = sum(v[0] for _, v in top) or 1

    stats = [
        ("Contributions (last year)", cc["contributionCalendar"]["totalContributions"]),
        ("Commits (last year)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("Pull requests", cc["totalPullRequestContributions"]),
        ("Public repos", repos["totalCount"]),
        ("Stars earned", stars),
    ]
    W, H = 840, 210
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="GitHub stats for {escape(u["name"] or "")}">',
         '<style>.f{animation:fi .6s ease-out both}@keyframes fi{from{opacity:0;transform:translateX(-6px)}to{opacity:1}}'
         '.b{animation:gr 1s ease-out both;transform-origin:left}@keyframes gr{from{transform:scaleX(0)}to{transform:scaleX(1)}}</style>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{C["bg"]}" stroke="{C["border"]}"/>',
         f'<text x="28" y="40" font-family="{SANS}" font-size="18" font-weight="600" fill="{C["title"]}">'
         f'⚡ {escape(u["name"] or "")}\'s GitHub Stats</text>']
    y = 76
    for i, (label, val) in enumerate(stats):
        s.append(f'<g class="f" style="animation-delay:{0.1 + i * 0.12:.2f}s">'
                 f'<circle cx="34" cy="{y - 5}" r="4" fill="{C["icon"]}"/>'
                 f'<text x="48" y="{y}" font-family="{SANS}" font-size="14" fill="{C["text"]}">{label}:</text>'
                 f'<text x="300" y="{y}" font-family="{SANS}" font-size="14" font-weight="700" fill="{C["value"]}" '
                 f'text-anchor="end">{fmt(val)}</text></g>')
        y += 27
    s.append(f'<path d="M340 30V{H - 30}" stroke="{C["border"]}"/>')
    s.append(f'<text x="370" y="40" font-family="{SANS}" font-size="18" font-weight="600" fill="{C["title"]}">'
             f'Top languages <tspan font-size="12" fill="{C["muted"]}">(public repos)</tspan></text>')
    bx, bw, by = 370, 440, 62
    s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="10" rx="5" fill="{C["bar_bg"]}"/>')
    s.append(f'<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)" class="b">')
    x = bx
    for name, (size, color) in top:
        w = bw * size / total
        s.append(f'<rect x="{x:.1f}" y="{by}" width="{w + 0.5:.1f}" height="10" fill="{color}"/>')
        x += w
    s.append("</g>")
    for i, (name, (size, color)) in enumerate(top):
        cx = bx + (i % 2) * 220
        cy = by + 40 + (i // 2) * 30
        s.append(f'<g class="f" style="animation-delay:{0.3 + i * 0.1:.2f}s"><circle cx="{cx + 6}" cy="{cy - 5}" r="6" fill="{color}"/>'
                 f'<text x="{cx + 20}" y="{cy}" font-family="{SANS}" font-size="14" fill="{C["text"]}">{escape(name)} '
                 f'<tspan fill="{C["muted"]}">{100 * size / total:.1f}%</tspan></text></g>')
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    login, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write(render(fetch(login)))
    print("wrote", out)
