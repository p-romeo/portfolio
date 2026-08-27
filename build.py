#!/usr/bin/env python3
CONTACT_EMAIL = "pauljromeo@proton.me"  # used in the Résumé section mailto link
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
    """Entries like: - **Name** | Issuer | Year | logo:path (optional)"""
    badges = []
    for line in md.splitlines():
        m = re.match(r"^- +\*\*(.+?)\*\* *\|([^|]+?)\|\s*([^|]+?)\s*(?:\|\s*(.+?)\s*)?$", line)
        if m:
            extra = (m.group(4) or "").strip()
            first = extra.split("|")[0].strip() if extra else ""
            logo = first[5:] if first.startswith("logo:") else ""
            badges.append({"name": m.group(1), "issuer": m.group(2).strip(),
                           "year": m.group(3), "url": "" if logo else first, "logo": logo})
    # optional credential_id / verify_url fields appended after the first 4 pipe groups
    for line in md.splitlines():
        m = re.match(r"^- +\*\*(.+?)\*\* *\|", line)
        if not m:
            continue
        for b in badges:
            if b["name"] == m.group(1):
                cid = re.search(r"\|\s*credential_id:([^|]+)", line)
                vurl = re.search(r"\|\s*verify_url:(\S+)", line)
                ico = re.search(r"\|\s*icon_text:([^|]+)", line)
                if cid:
                    b["credential_id"] = cid.group(1).strip()
                if vurl:
                    b["verify_url"] = vurl.group(1).strip()
                if ico:
                    b["icon_text"] = ico.group(1).strip()
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
            cur = {"title": h.group(1), "body": [], "logo": ""}
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
nav a{color:var(--muted);white-space:nowrap}
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
.card,.badge,.xp{transition:border-color .2s,transform .2s,box-shadow .2s}
.card:hover{border-color:var(--accent2);box-shadow:0 4px 18px rgba(79,195,247,.15)}
.badge:hover,.xp:hover{border-color:var(--accent);box-shadow:0 4px 18px rgba(61,220,151,.15)}
nav a.active{color:var(--accent);border-bottom:1px solid var(--accent)}
nav a.active::after{content:'_';animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.typed-cursor{display:inline-block;color:var(--accent);animation:blink 1s steps(1) infinite}
/* --- 3d constellation --- */
#space-wrap{position:relative;height:460px;border:1px solid var(--line);border-radius:12px;background:#070a0e;overflow:hidden;margin-bottom:8px}
#space-wrap canvas{display:block;width:100%;height:100%;cursor:grab}
#space-wrap canvas:active{cursor:grabbing}
#skill-label{position:absolute;left:14px;bottom:12px;font-family:var(--mono);font-size:.78rem;color:var(--accent);background:rgba(7,10,14,.85);border:1px solid var(--line);border-radius:6px;padding:5px 10px;pointer-events:none;opacity:0;transition:opacity .15s}
#skill-hint{position:absolute;right:12px;top:10px;font-family:var(--mono);font-size:.68rem;color:var(--muted)}
@media(max-width:720px){#space-wrap{height:380px}}
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


def render():
    about_md = read("about.md")
    certs = parse_certs(read("certifications.md"))
    projects = parse_projects()
    skills = parse_skills(read("skills.md"))
    experience = parse_experience(read("experience.md"))

    nav = "".join(f'<a href="#{sid}">{label}</a>' for sid, label in [
        ("about", "about"), ("experience", "experience"), ("certifications", "certs"),
        ("projects", "projects"), ("skills", "skills"), ("resume", "resume")])

    hero_tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in [
        "B.S. Cybersecurity — WGU", "SSCP", "Security+", "CySA+", "PenTest+", "Incident Response", "SOC"])

    facts = """
<dl class="facts">
<dt>Currently</dt><dd>IT Director &amp; Security Manager, Belmont Leather Co.</dd>
<dt>Education</dt><dd>B.S. Cybersecurity &amp; Information Assurance, WGU — graduated Aug 2026</dd>
<dt>Incident Response</dt><dd>Phishing &amp; BEC investigation; attacker infrastructure takedowns</dd>
<dt>Focus</dt><dd>Incident response &middot; SOC operations &middot; Detection engineering</dd>
<dt>Founder</dt><dd>Shoe and Boot Accessories 4 U (Amazon / eBay / BigCommerce)</dd>
</dl>"""

    def xp_logo(r):
        org = r["title"].split("—")[0].strip() or "Employer"
        logos = r.get("logo", "")
        if isinstance(logos, str):
            logos = [(logos, "")] if logos else []
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
    if os.path.exists('Paul-Romeo-Resume.pdf'):
        shutil.copy('Paul-Romeo-Resume.pdf', 'site/Paul-Romeo-Resume.pdf')
    badges_html = "".join(badge_card(i, b) for i, b in enumerate(certs))

    cards_html = ""
    for idx, p in enumerate(projects):
        link = p.get("link", "")
        site = p.get("site", "")
        title = esc(p.get("title", ""))
        if link and link != "private":
            title = f'<a href="{esc(link)}">{title}</a>'
        priv = ' <span class="chip">private repo</span>' if link == "private" else ""
        body_html = blocks(p["body"])
        site_link = (f' <a class="chip" href="{esc(site)}" style="text-decoration:none">'
                     f'{esc(site.split("//", 1)[-1].split("/")[0])} ↗</a>' if site else "")
        cards_html += (
            f'<article class="card" data-reveal style="--d:{idx * 40}ms"><div class="meta">{esc(p.get("tag", ""))}</div>'
            f'<h3>{title}{priv}{site_link}</h3>{body_html}</article>')

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
var links=[].slice.call(document.querySelectorAll('nav a[href^="#"]'));
var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a;});
if('IntersectionObserver' in window){
 var nio=new IntersectionObserver(function(es){es.forEach(function(e){
  var a=map[e.target.id];if(!a)return;
  if(e.isIntersecting){links.forEach(function(l){l.classList.remove('active');});a.classList.add('active');}
 });},{rootMargin:'-45% 0px -50% 0px'});
 Object.keys(map).forEach(function(id){var s=document.getElementById(id);if(s)nio.observe(s);});
}
// hero typing
var roles=['phishing investigation','EDR management','abuse-desk takedowns','SIEM & detection'];
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
}else if(el){el.textContent='phishing investigation · EDR · takedowns';}
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

    # ---- 3d skills constellation (three.js) ----
    import json
    palette = ["#3ddc97", "#4fc3f7", "#f7b74f", "#e46bd8", "#8f7bff", "#6ee7c8"]
    constellation_data = [
        {"category": g["category"], "items": g["items"], "color": palette[i % len(palette)]}
        for i, g in enumerate(skills)]
    SKILL_DATA_JSON = json.dumps(constellation_data).replace("</", "<\\/")

    SPACE_JS_TEMPLATE = """<script type="module">
(async function(){
'use strict';
const wrap=document.getElementById('space-wrap'),canvas=document.getElementById('skill-space'),label=document.getElementById('skill-label');
if(!wrap||!canvas)return;
const DATA=__SKILL_DATA__;
function init(){
 const THREE=window.__THREE__;if(!THREE)return;
 const scene=new THREE.Scene();
 const camera=new THREE.PerspectiveCamera(50,wrap.clientWidth/wrap.clientHeight,.1,100);
 camera.position.set(0,4,15);
 const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,2));
 renderer.setSize(wrap.clientWidth,wrap.clientHeight,false);
 scene.add(new THREE.AmbientLight(0xffffff,.5));
 const key=new THREE.DirectionalLight(0xffffff,.9);key.position.set(5,10,7);scene.add(key);
 // clusters
 const N=DATA.reduce((s,g)=>s+g.items.length,0),rows=[],meta=[];
 let id=0;
 DATA.forEach((g,gi)=>{
  const a=gi/DATA.length*Math.PI*2,cx=Math.cos(a)*6.2,cz=Math.sin(a)*6.2;
  const nodes=[];
  g.items.forEach((name,i)=>{
   const t=i/g.items.length,r=1.9,nth=g.items.length;
   const x=cx+Math.cos(t*Math.PI*2+nth)*r*(0.55+0.3*Math.sin(i*2.7)),z=cz+Math.sin(t*Math.PI*2+nth)*r*(0.55+0.3*Math.cos(i*1.9)),y=(i%2?.9:-.9)*(0.4+t*.25);
   const geo=new THREE.IcosahedronGeometry(.28,0);
   const mat=new THREE.MeshStandardMaterial({color:g.color,emissive:new THREE.Color(g.color),emissiveIntensity:.35,roughness:.35,metalness:.15});
   const m=new THREE.Mesh(geo,mat);m.position.set(x,y,z);scene.add(m);nodes.push(m);
   meta.push({mesh:m,name:name,cat:g.category,color:g.color,id:id++});
  });
  rows.push({nodes:nodes,color:g.color,angle:a});
 });
 // spokes + cluster rings
 const lineMat=new THREE.LineBasicMaterial({color:0x223042,transparent:true,opacity:.85});
 rows.forEach(row=>{
  for(let i=1;i<row.nodes.length;i++){
   const g2=new THREE.BufferGeometry().setFromPoints([row.nodes[i-1].position,row.nodes[i].position]);
   scene.add(new THREE.Line(g2,lineMat));
  }
  const ringG=new THREE.BufferGeometry().setFromPoints(
   Array.from({length:49},(_,k)=>{const t=k/48*Math.PI*2;return new THREE.Vector3(Math.cos(t)*6.2,-1.6,Math.sin(t)*6.2)}));
  const rm=new THREE.LineBasicMaterial({color:new THREE.Color(row.color),transparent:true,opacity:.18});
  scene.add(new THREE.Line(ringG,rm));
 });
 // starfield (shared geometry)
 const sGeo=new THREE.BufferGeometry(),n=350,pos=new Float32Array(n*3);
 for(let i=0;i<n;i++){pos[i*3]=(Math.random()-.5)*46;pos[i*3+1]=(Math.random()-.5)*26;pos[i*3+2]=(Math.random()-.5)*46;}
 sGeo.setAttribute('position',new THREE.BufferAttribute(pos,3));
 scene.add(new THREE.Points(sGeo,new THREE.PointsMaterial({color:0x4fc3f7,size:.06,transparent:true,opacity:.5})));
 // orbit control (drag + wheel zoom + touch pinch)
 const target=new THREE.Vector3(0,0,0);let theta=.6,phi=1.15,radius=17,vTheta=0;
 function apply(){camera.position.set(radius*Math.sin(phi)*Math.sin(theta),radius*Math.cos(phi),radius*Math.sin(phi)*Math.cos(theta));camera.lookAt(target);}
 apply();
 let dragging=false,lx=0,ly=0,touchDist=0;
 canvas.addEventListener('pointerdown',e=>{dragging=true;lx=e.clientX;ly=e.clientY;canvas.setPointerCapture(e.pointerId);});
 canvas.addEventListener('pointermove',e=>{
  if(dragging){theta-=(e.clientX-lx)*.005;phi+=(e.clientY-ly)*.005;phi=Math.max(.35,Math.min(2.65,phi));lx=e.clientX;ly=e.clientY;}
  else pick(e);
 });
 addEventListener('pointerup',()=>dragging=false,{passive:true});
 canvas.addEventListener('wheel',e=>{e.preventDefault();radius=Math.max(9,Math.min(30,radius+e.deltaY*.02));},{passive:false});
 canvas.addEventListener('touchmove',e=>{if(e.touches.length===2){const dx=e.touches[0].clientX-e.touches[1].clientX,dy=e.touches[0].clientY-e.touches[1].clientY,d=Math.hypot(dx,dy);if(touchDist)radius=Math.max(9,Math.min(30,radius-(d-touchDist)*.03));touchDist=d;}},{passive:true});
 canvas.addEventListener('touchend',()=>touchDist=0,{passive:true});
 // hover raycast
 const ray=new THREE.Raycaster(),ptr=new THREE.Vector2();let hovered=null;
 function pick(e){
  const r=canvas.getBoundingClientRect();
  ptr.x=((e.clientX-r.left)/r.width)*2-1;ptr.y=-((e.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(meta.map(m=>m.mesh))[0];
  const found=hit&&meta.find(m=>m.mesh===hit.object)||null;
  if(found!==hovered){
   if(hovered){hovered.mesh.material.emissiveIntensity=.35;hovered.mesh.scale.setScalar(1);}
   hovered=found;
   if(hovered){hovered.mesh.material.emissiveIntensity=.95;hovered.mesh.scale.setScalar(1.45);
    label.textContent='> '+hovered.name+' ['+hovered.cat+']';label.style.opacity=1;}
   else label.style.opacity=0;
   canvas.style.cursor=hovered?'pointer':'grab';
  }
 }
 // visibility-gated animation
 let visible=false,inited=true;
 new IntersectionObserver(es=>es.forEach(e=>{visible=e.isIntersecting;}),{threshold:.05}).observe(wrap);
 document.addEventListener('visibilitychange',()=>{});
 function loop(t){
  requestAnimationFrame(loop);
  if(!visible)return;
  const s=t*.001;
  vTheta+= .00035;
  theta+=vTheta*.016;if(!dragging)vTheta=Math.min(vTheta+.0002,.004);
  meta.forEach((m,i)=>{
   if(m!==hovered)m.mesh.position.y+=Math.sin(s*1.2+i)*.0012;
  });
  apply();
  renderer.render(scene,camera);
 }
 requestAnimationFrame(loop);
 // resize
 let rz=0;new ResizeObserver(()=>{if(!rz)rz=requestAnimationFrame(()=>{rz=0;
  const w=wrap.clientWidth,h=wrap.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);});}).observe(wrap);
}
if(matchMedia('(prefers-reduced-motion: reduce)').matches){wrap.style.display='none';return;}
// lazy-load three.js only when section approaches viewport
let started=false;
const io=new IntersectionObserver(es=>es.forEach(async e=>{
 if(!e.isIntersecting||started)return;started=true;io.disconnect();
 try{
  const T=await import('https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js');
  window.__THREE__=T;init();
 }catch(err){/* CDN blocked: keep chips-only fallback */}
}),{rootMargin:'400px 0px'});
io.observe(wrap);
})();
</script>"""
    SPACE_JS = SPACE_JS_TEMPLATE.replace("__SKILL_DATA__", SKILL_DATA_JSON)

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
<div id="progress" aria-hidden="true"></div>
<header><div class="wrap"><nav><span class="brand">paul_romeo</span>{nav}</nav></div></header>

<div class="hero" data-reveal><div class="wrap">
<div class="kicker">// cybersecurity · defensive security</div>
<h1>Paul Joseph Romeo</h1>
<p class="sub">Security manager who does the work — incident response, takedowns, endpoint &amp; network defense.</p>
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

<section id="projects"><div class="wrap">
<h2>Projects</h2>
<div class="cards">{cards_html}</div>
</div></section>

<section id="skills"><div class="wrap">
<h2>Skills</h2>
<div id="space-wrap">
<canvas id="skill-space"></canvas>
<div id="skill-hint">drag to orbit · scroll to zoom · hover nodes</div>
<div id="skill-label"></div>
</div>
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

<footer><div class="wrap">built with a tiny static generator <span class="sep">|</span> markdown in, html out <span class="sep">|</span> © 2026 Paul Joseph Romeo</footer>
{JS}
{SPACE_JS}
</body></html>"""

    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    # copy static assets (logos) into site/
    import shutil
    assets_src = os.path.join(ROOT, "assets")
    if os.path.isdir(assets_src):
        shutil.copytree(assets_src, os.path.join(SITE, "assets"), dirs_exist_ok=True)
    print(f"Wrote {os.path.join(SITE, 'index.html')} ({len(page)} bytes, {len(certs)} certs, {len(projects)} projects)")


if __name__ == "__main__":
    render()
