#!/usr/bin/env python3
CONTACT_EMAIL = "pauljromeo@proton.me"  # used in the Résumé section mailto link
"""Portfolio site generator.

Renders markdown content from content/ into a single-page static site in site/.
Stdlib only — no dependencies. Run: python3 build.py
"""
import html
import os
import re
import time

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
    """Entries like: - **Name** | Issuer | Year | logo:path (optional)"""
    badges = []
    for line in md.splitlines():
        m = re.match(r"^- +\*\*(.+?)\*\* *\|([^|]+?)\|\s*([^|]+?)\s*(?:\|\s*(.+?)\s*)?$", line)
        if m:
            extra = (m.group(4) or "").strip()
            first = extra.split("|")[0].strip() if extra else ""
            logo = first[5:] if first.startswith("logo:") else ""
            badges.append({"name": m.group(1), "issuer": m.group(2).strip(),
                           "year": m.group(3), "logo": logo})
            for field in ('credential_id', 'verify_url', 'icon_text'):
                value = re.search(r'\|\s*' + field + r':([^|]+)', line)
                if value:
                    badges[-1][field] = value.group(1).strip()
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
    # drop hidden projects, then sort by weight then name
    projects = [p for p in projects if str(p.get("hidden", "")).lower() != "true"]
    projects.sort(key=lambda p: (int(p.get("weight", 99)), p.get("title", "")))
    return projects


def parse_experience(md):
    """## Role — Org (dates), optional `logo:path` line, then paragraph(s)."""
    roles, cur = [], None
    for line in md.splitlines():
        h = re.match(r"^##\s+(.+)", line)
        if h:
            cur = {"title": h.group(1), "body": [], "logo": []}
            roles.append(cur)
        elif cur is not None and line.strip():
            lm = re.match(r"^logo:(.+)$", line.strip())
            if lm:
                # Comma-separated paths; each may carry "|alt text".
                cur["logo"] = [
                    p.split("|", 1) if "|" in p else (p.strip(), "")
                    for p in lm.group(1).split(",")
                ]
            else:
                cur["body"].append(line.strip())
    for r in roles:
        r["body"] = " ".join(r["body"])
    return roles


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
nav{display:flex;align-items:center;flex-wrap:wrap;row-gap:8px;gap:16px;padding:16px 0;font-family:var(--mono);font-size:.85rem}
nav .brand{color:var(--accent);font-weight:700;margin-right:auto}
@media(max-width:720px){nav .brand{flex-basis:100%;margin-right:0}}
nav .brand::before{content:'>_ '}
nav a{color:var(--muted);white-space:nowrap}nav a:hover{color:var(--accent)}
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
.badges{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.badge{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;transition:border-color .2s,transform .2s}
.badge:hover{border-color:var(--accent);transform:translateY(-2px)}
.badge .icon{width:56px;height:44px;flex:none;border-radius:9px;display:flex;align-items:center;justify-content:center;background:#f5f7fa;border:1px solid var(--line);font-family:var(--mono);font-weight:700;color:var(--accent);font-size:.95rem;padding:6px}
.badge .icon img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.badge>div{min-width:0}
.badge b{display:block;font-size:.92rem;line-height:1.25}
.badge span{font-size:.78rem;color:var(--muted)}
.badge span:not(.cid){display:block;line-height:1.35}
.badge .cid{display:block;font-family:var(--mono);font-size:.68rem;color:var(--muted);margin-top:4px;letter-spacing:.02em;word-break:break-all}
.badge .verify-link{color:inherit;text-decoration:none;border-bottom:1px dotted var(--muted)}
.badge .verify-link:hover{color:var(--accent);border-bottom-color:var(--accent)}
.badge .verify-link::after{content:" ↗";font-size:.75em}
.skill-group{margin-bottom:20px}
.skill-group h3{font-family:var(--mono);font-size:.78rem;color:var(--accent2);text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.xp{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:14px}
.xp-head{display:flex;align-items:center;gap:14px}
.xp-logo{width:96px;height:44px;flex:none;border-radius:9px;display:flex;align-items:center;justify-content:center;background:#f5f7fa;border:1px solid var(--line);padding:6px;gap:4px}
.xp-logo img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.xp-logo.multi{padding:6px 4px}
.xp-logo.multi img{width:40px;height:32px;flex:none}
.xp h3{font-size:1rem;margin-bottom:6px}
.xp p{font-size:.9rem;color:var(--muted)}
.chip{font-family:var(--mono);font-size:.75rem;background:var(--bg2);border:1px solid var(--line);border-radius:6px;padding:4px 10px;color:var(--text)}
.resume-card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:28px;display:flex;align-items:center;gap:28px;flex-wrap:wrap}
.btn{font-family:var(--mono);font-size:.85rem;padding:11px 22px;border-radius:8px;border:1px solid var(--accent);color:var(--bg);background:var(--accent);font-weight:700}
.btn:hover{text-decoration:none;filter:brightness(1.1)}
.btn.ghost{background:transparent;color:var(--accent)}
footer{padding:32px 0;font-family:var(--mono);font-size:.78rem;color:var(--muted);text-align:center}
footer .sep{color:var(--line)}
/* --- interactive polish --- */
html{scroll-padding-top:64px}
#progress{position:fixed;top:0;left:0;height:2px;width:100%;transform-origin:0 50%;transform:scaleX(0);background:var(--accent);z-index:20;box-shadow:0 0 6px rgba(61,220,151,.6);will-change:transform}
[data-reveal]{opacity:0;transform:translateY(18px)}
[data-reveal].in{opacity:1;transform:none;transition:opacity .5s ease,transform .5s ease;transition-delay:var(--d,0ms)}
.badge,.xp{transition:border-color .2s,transform .2s,box-shadow .2s}
.badge:hover,.xp:hover{border-color:var(--accent);box-shadow:0 4px 18px rgba(61,220,151,.15)}
nav a.active{color:var(--accent);border-bottom:1px solid var(--accent)}
nav a.active::after{content:'_';animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.typed-cursor{display:inline-block;color:var(--accent);animation:blink 1s steps(1) infinite}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
 @media(prefers-reduced-motion:reduce){
 html{scroll-behavior:auto}
 [data-reveal]{opacity:1;transform:none}
 [data-reveal].in{transition:none}
 nav a.active::after,.typed-cursor{animation:none}
 *{scroll-behavior:auto!important}
}
"""


def esc(s):
    return html.escape(str(s))


def render_header(current=""):
    links = "".join(
        f'<a href="{href}"' + (' class="active" aria-current="page"' if label == current else '')
        + f'>{label}</a>'
        for href, label in [("/#about", "about"), ("/#experience", "experience"),
                            ("/#certifications", "certs"), ("/projects/", "projects"),
                            ("/#skills", "skills"), ("/#resume", "resume")])
    return f'<header><div class="wrap"><nav><a class="brand" href="/">paul_romeo</a>{links}</nav></div></header>'


FOOTER = '<footer><div class="wrap">built with a tiny static generator <span class="sep">|</span> markdown in, html out <span class="sep">|</span> © 2026 Paul Joseph Romeo</div></footer>'


FAVICONS = '''<link rel="icon" href="/assets/icons/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" href="/assets/icons/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png" sizes="180x180">'''


def render_projects_page(projects):
    """Standalone projects page using the homepage's CSS foundation."""
    # per-project accent colors: each card gets its own hue (border/glow/tag/title)
    PROJECT_COLORS = [
        "#3ddc97",  # green
        "#4fc3f7",  # cyan
        "#b388ff",  # purple
        "#ff8a65",  # coral
        "#ffd54f",  # amber
        "#4dd0e1",  # teal
        "#f06292",  # pink
        "#aed581",  # lime
        "#90a4ae",  # steel
    ]
    cards = []
    for idx, p in enumerate(projects):
        accent = PROJECT_COLORS[idx % len(PROJECT_COLORS)]
        accent_style = f'style="--pc:{accent}"'
        link, site = p.get("link", ""), p.get("site", "")
        title = esc(p.get("title", ""))
        if link and link != "private":
            title = f'<a href="{esc(link)}">{title}</a>'
        private = ' <span class="private">private repo</span>' if link == "private" else ""
        links = []
        if site:
            host = esc(site.split("//", 1)[-1].split("/")[0])
            links.append(f'<a href="{esc(site)}">{host} <span aria-hidden="true">↗</span></a>')
        if link and link != "private" and "github.com" in link:
            links.append(f'<a href="{esc(link)}">source <span aria-hidden="true">↗</span></a>')
        featured = ' featured' if str(p.get("weight")) == '1' else ''
        cards.append(f"""<article class="xp project{featured}" {accent_style}>
<div class="project-tag">{esc(p.get('tag', ''))}</div>
<h3>{title}{private}</h3>
<div class="project-body">{blocks(p['body'])}</div>
<div class="project-links">{''.join(links)}</div>
</article>""")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{FAVICONS}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Projects — Paul Joseph Romeo</title>
<meta name="description" content="Projects by Paul Joseph Romeo: detection tooling, security automation, and applied AI systems.">
<style>{CSS}
.projects-grid{{display:grid;gap:14px}}
.project{{margin:0;min-width:0}}.project h3{{margin:8px 0}}.project h3 a{{color:inherit}}
.project h3 a:hover{{color:var(--accent2)}}
.project-tag{{font: .75rem var(--mono);color:var(--accent);letter-spacing:.12em;text-transform:uppercase}}
.project-body{{font-size:.9rem;color:var(--muted);overflow-wrap:anywhere}}
.project-body p{{margin-bottom:8px}}.project-body ul{{padding-left:20px}}.project-body code{{color:var(--accent2)}}
.project-links{{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}}
.project-links a,.private{{font: .75rem var(--mono);border:1px solid var(--line);border-radius:6px;padding:5px 10px;overflow-wrap:anywhere}}
.private{{font-size:.75rem;color:var(--muted);white-space:nowrap}}
/* per-project accent: each card sets --pc with its own hue */
.project{{--pc:var(--accent);border-top:2px solid var(--pc);border-radius:10px 10px 6px 6px}}
.project .project-tag{{color:var(--pc)}}
.project h3 a:hover{{color:var(--pc)}}
.project .project-links a{{border-color:color-mix(in srgb, var(--pc) 35%, var(--line));color:var(--pc)}}
.project .project-links a:hover{{border-color:var(--pc)}}
.project .project-body code{{color:var(--pc)}}
/* sink-tilt (adapted from bencho.dev, MIT): card presses AWAY from the cursor,
   a shadow-dent tracks the pointer, and the drop shadow tightens while pressed */
.project{{transform-style:preserve-3d;transition:transform .15s ease-out, box-shadow .15s ease-out;will-change:transform}}
@media (hover:hover) and (pointer:fine) and (prefers-reduced-motion:no-preference){{
.project.sink-active{{transition:transform .05s linear, box-shadow .05s linear;cursor:default}}}}
/* featured (weight 1) card: bold glow treatment using its own hue */
.project.featured{{border:1.5px solid var(--pc);background:linear-gradient(140deg, color-mix(in srgb, var(--pc) 16%, transparent), transparent 65%), #131a22;border-radius:12px;padding:18px;box-shadow:0 0 24px -6px var(--pc), inset 0 0 40px -20px var(--pc)}}
.project.featured .project-tag{{color:var(--pc);font-weight:bold}}
.project.featured .project-tag::before{{content:"\u2605 ";letter-spacing:0}}
.project.featured h3{{font-size:1.3rem}}
.project.featured h3 a{{color:var(--pc)}}
.project.featured h3 a:hover{{color:#fff}}
.project.featured .project-body{{color:#c9d6e2;font-size:.92rem}}
.project.featured .project-links a{{border-color:var(--pc);color:var(--pc)}}
</style>
</head>
<body>
{render_header("projects")}
<main>
<div class="hero"><div class="wrap">
<div class="kicker">// projects</div>
<h1>Things I've built.</h1><p class="sub">Detection tooling, security automation, and applied AI systems —
mostly born from real incident-response work. {len(projects)} projects.</p></div></div>
<section><div class="wrap"><h2>Projects</h2>
<div class="projects-grid">{''.join(cards)}</div>
</div></section>
</main>
{FOOTER}
<script>
/* sink-tilt (adapted from bencho.dev "Tilt card", MIT): the card sinks AWAY from
   the cursor instead of lifting; a dark dent-gradient tracks the pointer and the
   far rim catches light. Springs on position give it mass. Pointer-fine +
   reduced-motion-gated, matches the site's interaction layer rules. */
(function(){{
  var fine = matchMedia('(hover:hover) and (pointer:fine)').matches
          && !matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!fine) return;
  var TILT = 4, SHADOW_LIT = '0 10px 28px -12px rgba(0,0,0,.55)';
  document.querySelectorAll('.project').forEach(function(card){{
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null, on = false;
    function frame(){{
      cx += (tx - cx) * 0.18; cy += (ty - cy) * 0.18;
      var rx = (-cy) * TILT, ry = cx * TILT;
      card.style.transform = 'perspective(800px) rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg)';
      var X = ((cx + 1) * 50).toFixed(1), Y = ((cy + 1) * 50).toFixed(1);
      card.style.backgroundImage =
        'radial-gradient(42% 34% at ' + X + '% ' + Y + '%, rgba(0,0,0,.28), transparent),' +
        'radial-gradient(52% 42% at ' + (100 - X) + '% ' + (100 - Y) + '%, rgba(255,255,255,.07), transparent)';
      card.style.boxShadow = on ? '0 6px 16px -10px rgba(0,0,0,.5)' : SHADOW_LIT;
      if (Math.abs(tx - cx) <= .001 && Math.abs(ty - cy) <= .001 && !on) {{
        raf = null; card.style.transform = ''; card.style.backgroundImage = ''; card.style.boxShadow = '';
      }} else if (Math.abs(tx - cx) > .001 || Math.abs(ty - cy) > .001) {{
        raf = requestAnimationFrame(frame);
      }} else raf = null;
    }}
    function kick(){{ if (!raf) raf = requestAnimationFrame(frame); }}
    card.addEventListener('pointerenter', function(){{
      on = true; card.classList.add('sink-active'); kick();
    }});
    card.addEventListener('pointermove', function(e){{
      var r = card.getBoundingClientRect();
      tx = ((e.clientX - r.left) / r.width) * 2 - 1;
      ty = ((e.clientY - r.top) / r.height) * 2 - 1;
      kick();
    }});
    card.addEventListener('pointerleave', function(){{
      on = false; tx = 0; ty = 0; card.classList.remove('sink-active');
      card.style.backgroundImage = ''; card.style.transform = '';
      card.style.boxShadow = ''; kick();
    }});
  }});
}})();
</script>
</body></html>"""


def render():
    about_md = read("about.md")
    certs = parse_certs(read("certifications.md"))
    projects = parse_projects()
    skills = parse_skills(read("skills.md"))
    experience = parse_experience(read("experience.md"))

    hero_tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in [
        "B.S. Cybersecurity — WGU", "SSCP", "Security+", "CySA+", "PenTest+", "Incident Response", "Security monitoring"])

    facts = """
<dl class="facts">
<dt>Currently</dt><dd>IT Director &amp; Security Manager, Belmont Leather Co.</dd>
<dt>Education</dt><dd>B.S. Cybersecurity &amp; Information Assurance, WGU — graduated Aug 2026</dd>
<dt>Incident Response</dt><dd>Phishing defense &amp; email security; detection tooling; working toward full IR role</dd>
<dt>Focus</dt><dd>Incident response &middot; Security monitoring &middot; Detection engineering</dd>
<dt>Founder</dt><dd>Shoe and Boot Accessories 4 U (Amazon / eBay / BigCommerce)</dd>
</dl>"""

    def xp_logo(r):
        org = r["title"].split("—")[0].strip() or "Employer"
        logos = r["logo"]
        if logos:
            imgs = "".join(
                '<img src="%s" alt="%s logo" loading="lazy">'
                % (esc(path), esc(alt or org))
                for path, alt in logos
            )
            return '<div class="xp-logo multi">%s</div>' % imgs if len(logos) > 1 else '<div class="xp-logo">%s</div>' % imgs
        return ""

    experience_html = "".join(
        f'<div class="xp" data-reveal style="--d:{i * 40}ms"><div class="xp-head">{xp_logo(r)}<h3>{esc(r["title"])}</h3></div>'
        f'<p>{inline(r["body"])}</p></div>'
        for i, r in enumerate(experience))

    def badge_icon(b):
        logo = b.get("logo", "")
        if logo:
            return ('<div class="icon"><img src="%s" alt="%s logo" loading="lazy"></div>'
                    % (esc(logo), esc(b["issuer"])))
        return '<div class="icon">%s</div>' % esc(b.get("icon_text") or b["name"].split()[0][:3])

    def badge_card(i, b):
        title = esc(b["name"])
        if b.get("verify_url"):
            title = ('<a href="%s" target="_blank" rel="noopener" class="verify-link">%s</a>'
                     % (esc(b["verify_url"]), title))
        cid_line = ''
        if b.get("credential_id"):
            cid_line = '<span class="cid">ID: %s</span>' % esc(b["credential_id"])
        return (f'<div class="badge" data-reveal style="--d:{i * 40}ms">{badge_icon(b)}'
                f'<div><b>{title}</b><span>{esc(b["issuer"])} · {esc(b["year"])}</span>'
                f'{cid_line}</div></div>')

    import shutil
    os.makedirs(SITE, exist_ok=True)
    shutil.copy('tools/Paul-Romeo-Resume.docx', 'site/Paul-Romeo-Resume.docx')
    if os.path.exists('Paul-Romeo-Resume.pdf'):
        shutil.copy('Paul-Romeo-Resume.pdf', 'site/Paul-Romeo-Resume.pdf')
    badges_html = "".join(badge_card(i, b) for i, b in enumerate(certs))

    skills_html = "".join(
        f'<div class="skill-group" data-reveal style="--d:{i * 40}ms"><h3>{esc(g["category"])}</h3><div class="chips">'
        + "".join(f'<span class="chip">{esc(i)}</span>' for i in g["items"])
        + "</div></div>" for i, g in enumerate(skills))

    JS = """<script>
(function(){
'use strict';
var reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
// scroll reveals
var items=document.querySelectorAll('[data-reveal]');
if(!reduced&&'IntersectionObserver' in window){
 var io=new IntersectionObserver(function(es){es.forEach(function(e){
  if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}
 });},{threshold:.12,rootMargin:'0px 0px -40px 0px'});
 items.forEach(function(el){io.observe(el);});
}else{items.forEach(function(el){el.classList.add('in');});}
// active nav
var links=[].slice.call(document.querySelectorAll('nav a[href^="/#"]'));
var map={};links.forEach(function(a){map[a.getAttribute('href').slice(2)]=a;});
if('IntersectionObserver' in window){
 var nio=new IntersectionObserver(function(es){es.forEach(function(e){
  var a=map[e.target.id];if(!a)return;
  if(e.isIntersecting){links.forEach(function(l){l.classList.remove('active');});a.classList.add('active');}
 });},{rootMargin:'-45% 0px -50% 0px'});
 Object.keys(map).forEach(function(id){var s=document.getElementById(id);if(s)nio.observe(s);});
}
// hero typing
var roles=['phishing defense','EDR management','security monitoring','SIEM & detection'];
var el=document.getElementById('typed');
if(!reduced&&el){
 var ri=0,ci=0,del=false;
 (function tick(){
  var w=roles[ri];
  el.textContent=w.slice(0,ci);
  var t=del?40:75;
  if(!del&&ci===w.length){t=1600;del=true;}
  else if(del&&ci===0){del=false;ri=(ri+1)%roles.length;t=350;}
  else ci+=del?-1:1;
  setTimeout(tick,t);
 })();
}else if(el){el.textContent='phishing defense · EDR · security monitoring';}
// progress bar
var bar=document.getElementById('progress'),raf=0;
function upd(){
 raf=0;
 var h=document.documentElement;
 var max=h.scrollHeight-h.clientHeight;
 bar.style.transform='scaleX('+(max>0?(h.scrollTop||document.body.scrollTop)/max:1)+')';
}
addEventListener('scroll',function(){if(!raf)raf=requestAnimationFrame(upd);},{passive:true});
upd();
})();
</script>"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{FAVICONS}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Paul Joseph Romeo — Cybersecurity &amp; IT</title>
<meta name="description" content="Portfolio of Paul Joseph Romeo: IT Director &amp; Security Manager. SSCP, Security+, incident response, security monitoring, detection engineering.">
<style>{CSS}</style>
</head>
<body>
<div id="progress" aria-hidden="true"></div>
{render_header()}

<div class="hero" data-reveal><div class="wrap">
<div class="kicker">// cybersecurity · defensive security</div>
<h1>Paul Joseph Romeo</h1>
<p class="sub">Security manager who does the work — phishing defense, endpoint &amp; network security, and detection tooling.</p>
<p class="sub" style="font-family:var(--mono);color:var(--accent);font-size:1rem">&gt; <span id="typed">security manager</span><span class="typed-cursor">▌</span></p>
<div class="tags">{hero_tags}</div>
</div></div>

<section id="about"><div class="wrap" data-reveal>
<h2>About</h2>
<div class="about-grid"><div>{blocks(about_md)}</div>{facts}</div>
</div></section>

<section id="experience"><div class="wrap">
<h2>Experience</h2>
{experience_html}
</div></section>

<section id="certifications"><div class="wrap">
<h2>Certifications</h2>
<div class="badges">{badges_html}</div>
</div></section>

<section id="skills"><div class="wrap">
<h2>Skills</h2>
{skills_html}
</div></section>

<section id="resume"><div class="wrap" data-reveal>
<h2>Résumé</h2>
<div class="resume-card">
<div><b>Download a copy</b><br><span style="color:var(--muted);font-size:.9rem">PDF résumé, kept current.</span></div>
<a class="btn" href="Paul-Romeo-Resume.pdf" download>↓ Download PDF</a>
<a class="btn ghost" href="Paul-Romeo-Resume.docx" download>↓ Download Word</a>
<a class="btn ghost" href="mailto:{CONTACT_EMAIL}">✉ Contact me</a>
</div>
</div></section>

{FOOTER}
{JS}
</body></html>"""

    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)

    # ---- Projects page ----
    projects_page = render_projects_page(projects)
    os.makedirs(os.path.join(SITE, "projects"), exist_ok=True)
    with open(os.path.join(SITE, "projects", "index.html"), "w", encoding="utf-8") as f:
        f.write(projects_page)

    # robots.txt per RFC 9309 — plain text, agent/crawler directives, sitemap ref
    robots = "\n".join([
        "User-agent: *",
        "Allow: /",
        "",
        "Sitemap: https://paulromeo.net/sitemap.xml",
        "",
    ])
    with open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    # sitemap.xml per sitemaps.org protocol — canonical URLs of public pages
    lastmod = time.strftime("%Y-%m-%d")
    urls = [
        ("https://paulromeo.net/", "1.0"),
        ("https://paulromeo.net/projects/", "0.9"),
    ]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri in urls:
        sitemap.append("  <url>")
        sitemap.append(f"    <loc>{loc}</loc>")
        sitemap.append(f"    <lastmod>{lastmod}</lastmod>")
        sitemap.append(f"    <priority>{pri}</priority>")
        sitemap.append("  </url>")
    sitemap.append("</urlset>")
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap) + "\n")

    # llms.txt — machine-readable site summary (rel="describedby" target)
    llms = "\n".join([
        "# Paul Joseph Romeo — Cybersecurity & IT",
        "",
        "> Security manager at Belmont Leather Co: incident response, phishing/BEC",
        "> phishing defense, endpoint & network security, and building detection tooling.",
        "",
        "## Pages",
        "",
        "- [Home](https://paulromeo.net/): about, experience, certifications, skills, résumé",
        "- [Projects](https://paulromeo.net/projects/): " + ", ".join(p.get("title", "") for p in projects),
        "- [Résumé (PDF)](https://paulromeo.net/Paul-Romeo-Resume.pdf): current résumé, kept up to date",
        "",
        "## Contact",
        "",
        "- Email: pauljromeo@proton.me",
        "",
    ])
    with open(os.path.join(SITE, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(llms)
    # copy static assets (logos) into site/
    assets_src = os.path.join(ROOT, "assets")
    if os.path.isdir(assets_src):
        shutil.copytree(assets_src, os.path.join(SITE, "assets"), dirs_exist_ok=True)
    print(f"Wrote {os.path.join(SITE, 'index.html')} ({len(page)} bytes, {len(certs)} certs, {len(projects)} projects)")


if __name__ == "__main__":
    render()
