#!/usr/bin/env python3
# TODO(paul): set CONTACT_EMAIL — currently a placeholder (paul.j.romeo@example.com) used in the Résumé section mailto link.
"""Portfolio site generator.

Renders markdown content from content/ into a single-page static site in site/.
Stdlib only — no dependencies. Run: python3 build.py
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
SITE = os.path.join(ROOT, "site")


def read(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return f.read().strip()


def inline(md):
    """Minimal inline markdown -> HTML."""
    s = html.escape(md)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def blocks(md):
    """Very small markdown block renderer (headings, lists, paragraphs)."""
    out, lines = [], md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            level = len(m.group(1)) + 1
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue
        if re.match(r"^[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                items.append("<li>%s</li>" % inline(re.sub(r"^[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|[-*]\s)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(para)))
    return "\n".join(out)


# ---------- section parsers ----------

def parse_certs(md):
    """Entries like: - **Name** | Issuer | Year | badge-url(optional)"""
    badges = []
    for line in md.splitlines():
        m = re.match(r"^-\s+\*\*(.+?)\*\*\s+\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*(?:\|\s*(\S+)\s*)?$", line)
        if m:
            badges.append({"name": m.group(1), "issuer": m.group(2),
                           "year": m.group(3), "url": (m.group(4) or "").strip()})
    return badges


def parse_projects():
    """One markdown file per project in content/projects/, front-matter style header."""
    projects = []
    pdir = os.path.join(CONTENT, "projects")
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".md"):
            continue
        text = read(os.path.join("projects", fn))
        meta, body = {}, text
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if m:
            for ln in m.group(1).splitlines():
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = m.group(2).strip()
        meta["body"] = body
        projects.append(meta)
    # sort by weight then name
    projects.sort(key=lambda p: (int(p.get("weight", 99)), p.get("title", "")))
    return projects


def parse_skills(md):
    """## Category followed by comma-separated list."""
    groups, cur = [], None
    for line in md.splitlines():
        h = re.match(r"^##\s+(.+)", line)
        if h:
            cur = {"category": h.group(1), "items": []}
            groups.append(cur)
        elif cur is not None and line.strip() and not line.startswith("#"):
            cur["items"] += [x.strip() for x in line.split(",") if x.strip()]
    return groups


# ---------- render ----------

CSS = """:root{--bg:#0b0f14;--bg2:#10161e;--card:#131a23;--line:#223042;--text:#d7e2ee;
--muted:#8aa0b6;--accent:#3ddc97;--accent2:#4fc3f7;--mono:'SFMono-Regular',ui-monospace,Menlo,Consolas,monospace}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font:16px/1.65 'Segoe UI',system-ui,-apple-system,sans-serif}
a{color:var(--accent2);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:960px;margin:0 auto;padding:0 24px}
header{position:sticky;top:0;z-index:10;background:rgba(11,15,20,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
nav{display:flex;align-items:center;gap:24px;padding:16px 0;font-family:var(--mono);font-size:.85rem}
nav .brand{color:var(--accent);font-weight:700;margin-right:auto}
nav .brand::before{content:'>_ '}
nav a{color:var(--muted)}nav a:hover{color:var(--accent)}
.hero{padding:88px 0 64px;border-bottom:1px solid var(--line);
 background:radial-gradient(600px 300px at 70% 0%,rgba(79,195,247,.08),transparent),radial-gradient(500px 260px at 20% 100%,rgba(61,220,151,.07),transparent)}
.hero .kicker{font-family:var(--mono);color:var(--accent);font-size:.85rem;letter-spacing:.12em;text-transform:uppercase}
.hero h1{font-size:2.6rem;line-height:1.15;margin:12px 0 6px}
.hero .sub{font-size:1.15rem;color:var(--muted)}
.hero .tags{margin-top:18px;display:flex;flex-wrap:wrap;gap:8px}
.tag{font-family:var(--mono);font-size:.75rem;color:var(--accent);border:1px solid var(--line);background:var(--bg2);border-radius:999px;padding:4px 12px}
section{padding:56px 0;border-bottom:1px solid var(--line)}
h2{font-size:1.5rem;margin-bottom:24px;display:flex;align-items:center;gap:12px}
h2::before{content:'//';font-family:var(--mono);color:var(--accent);font-size:1rem}
.about-grid{display:grid;grid-template-columns:2fr 1fr;gap:36px}
@media(max-width:720px){.about-grid{grid-template-columns:1fr}.hero h1{font-size:2rem}}
.about-grid p{margin-bottom:14px;color:var(--text)}
.facts{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;font-size:.9rem}
.facts dt{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;color:var(--accent);letter-spacing:.1em;margin-top:12px}
.facts dt:first-child{margin-top:0}.facts dd{color:var(--muted)}
.badges{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.badge{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;transition:border-color .2s,transform .2s}
.badge:hover{border-color:var(--accent);transform:translateY(-2px)}
.badge .icon{width:38px;height:38px;flex:none;border-radius:9px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#17324a,#12301f);font-family:var(--mono);font-weight:700;color:var(--accent);font-size:.95rem}
.badge b{display:block;font-size:.92rem}
.badge span{font-size:.78rem;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;display:flex;flex-direction:column;transition:border-color .2s,transform .2s}
.card:hover{border-color:var(--accent2);transform:translateY(-2px)}
.card h3{font-size:1.05rem;margin-bottom:4px}
.card .meta{font-family:var(--mono);font-size:.72rem;color:var(--accent);text-transform:uppercase;letter-spacing:.1em}
.card p{font-size:.9rem;color:var(--muted);margin-top:10px;flex-grow:1}
.card ul{margin-top:10px;padding-left:18px;font-size:.85rem;color:var(--muted)}
.card ul li{margin-bottom:3px}
.skill-group{margin-bottom:20px}
.skill-group h3{font-family:var(--mono);font-size:.78rem;color:var(--accent2);text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{font-family:var(--mono);font-size:.75rem;background:var(--bg2);border:1px solid var(--line);border-radius:6px;padding:4px 10px;color:var(--text)}
.resume-card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:28px;display:flex;align-items:center;gap:28px;flex-wrap:wrap}
.btn{font-family:var(--mono);font-size:.85rem;padding:11px 22px;border-radius:8px;border:1px solid var(--accent);color:var(--bg);background:var(--accent);font-weight:700}
.btn:hover{text-decoration:none;filter:brightness(1.1)}
.btn.ghost{background:transparent;color:var(--accent)}
footer{padding:32px 0;font-family:var(--mono);font-size:.78rem;color:var(--muted);text-align:center}
footer .sep{color:var(--line)}
"""


def esc(s):
    return html.escape(str(s))


def render():
    about_md = read("about.md")
    certs = parse_certs(read("certifications.md"))
    projects = parse_projects()
    skills = parse_skills(read("skills.md"))

    nav = "".join(f'<a href="#{sid}">{label}</a>' for sid, label in [
        ("about", "about"), ("certifications", "certs"),
        ("projects", "projects"), ("skills", "skills"), ("resume", "resume")])

    hero_tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in [
        "SSCP", "Security+", "Incident Response", "SOC", "Detection Engineering"])

    facts = """
<dl class="facts">
<dt>Currently</dt><dd>IT Director &amp; Security Manager, Belmont Leather Co.</dd>
<dt>Education</dt><dd>B.S. Cybersecurity &amp; Information Assurance, WGU — graduated Aug 2026</dd>
<dt>Incident Response</dt><dd>Phishing &amp; BEC investigation; attacker infrastructure takedowns</dd>
<dt>Focus</dt><dd>Incident response &middot; SOC operations &middot; Detection engineering</dd>
<dt>Founder</dt><dd>Shoe and Boot Accessories 4 U (Amazon / eBay / BigCommerce)</dd>
</dl>"""

    badges_html = "".join(
        f'<div class="badge"><div class="icon">{esc(b["name"].split()[0][:3])}</div>'
        f'<div><b>{esc(b["name"])}</b><span>{esc(b["issuer"])} · {esc(b["year"])}</span></div></div>'
        for b in certs)

    cards_html = ""
    for p in projects:
        link = p.get("link", "")
        title = esc(p.get("title", ""))
        if link and link != "private":
            title = f'<a href="{esc(link)}">{title}</a>'
        priv = ' <span class="chip">private repo</span>' if link == "private" else ""
        body_html = blocks(p["body"])
        cards_html += (
            f'<article class="card"><div class="meta">{esc(p.get("tag", ""))}</div>'
            f'<h3>{title}{priv}</h3>{body_html}</article>')

    skills_html = "".join(
        f'<div class="skill-group"><h3>{esc(g["category"])}</h3><div class="chips">'
        + "".join(f'<span class="chip">{esc(i)}</span>' for i in g["items"])
        + "</div></div>" for g in skills)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Paul Joseph Romeo — Cybersecurity &amp; IT</title>
<meta name="description" content="Portfolio of Paul Joseph Romeo: IT Director &amp; Security Manager. SSCP, Security+, incident response, SOC operations, detection engineering.">
<style>{CSS}</style>
</head>
<body>
<header><div class="wrap"><nav><span class="brand">paul_romeo</span>{nav}</nav></div></header>

<div class="hero"><div class="wrap">
<div class="kicker">// cybersecurity · defensive security</div>
<h1>Paul Joseph Romeo</h1>
<p class="sub">IT Director &amp; Security Manager turning operational leadership into defensible security.</p>
<div class="tags">{hero_tags}</div>
</div></div>

<section id="about"><div class="wrap">
<h2>About</h2>
<div class="about-grid"><div>{blocks(about_md)}</div>{facts}</div>
</div></section>

<section id="certifications"><div class="wrap">
<h2>Certifications</h2>
<div class="badges">{badges_html}</div>
</div></section>

<section id="projects"><div class="wrap">
<h2>Projects</h2>
<div class="cards">{cards_html}</div>
</div></section>

<section id="skills"><div class="wrap">
<h2>Skills</h2>
{skills_html}
</div></section>

<section id="resume"><div class="wrap">
<h2>Résumé</h2>
<div class="resume-card">
<div><b>Download a copy</b><br><span style="color:var(--muted);font-size:.9rem">PDF résumé, kept current.</span></div>
<!-- TODO(paul): upload Paul-Romeo-Resume.pdf to site/ so this download link works -->
<a class="btn" href="Paul-Romeo-Resume.pdf" download>↓ Download PDF</a>
<a class="btn ghost" href="mailto:paul.j.romeo@example.com">✉ Contact me</a>
</div>
</div></section>

<footer><div class="wrap">built with a tiny static generator <span class="sep">|</span> markdown in, html out <span class="sep">|</span> © 2026 Paul Joseph Romeo</footer>
</body></html>"""

    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {os.path.join(SITE, 'index.html')} ({len(page)} bytes, {len(certs)} certs, {len(projects)} projects)")


if __name__ == "__main__":
    render()
