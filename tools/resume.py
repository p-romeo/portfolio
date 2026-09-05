"""Generate Paul Romeo's one-page ATS-friendly resume PDF (fpdf2).

Content mirrors tools/resume_spec.json (the .docx version).
"""
from fpdf import FPDF

PDF = "Paul-Romeo-Resume.pdf"

pdf = FPDF(format="letter", unit="pt")
# Liberation Sans: clean Arial-metric font with em-dash support
pdf.add_font("liberation", "", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
pdf.add_font("liberation", "B", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
pdf.set_margins(36, 36, 36)
pdf.add_page()
W = pdf.w - 80  # usable width

DARK = (25, 30, 38)
ACCENT = (30, 70, 120)

def h1(text):
    pdf.set_font("liberation", "B", 20)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 22, text, new_x="LMARGIN", new_y="NEXT")

def contact_line():
    pdf.set_font("liberation", "", 10)
    pdf.set_text_color(70, 78, 90)
    pdf.cell(0, 13, "Union, NJ  |  pauljromeo@proton.me  |  linkedin.com/in/paul-romeo  |  github.com/p-romeo",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

def section(title):
    y = pdf.get_y() + 2
    pdf.set_font("liberation", "B", 12)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 14, title.upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.7)
    pdf.line(40, y + 14, 40 + W, y + 14)
    pdf.ln(3.5)

def para(text, size=10, style="", h=13):
    pdf.set_font("liberation", style, size)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(W, h, text, new_x="LMARGIN", new_y="NEXT", align="L")

def skill_line(label, text):
    pdf.set_font("liberation", "B", 10)
    pdf.set_text_color(*DARK)
    lw = pdf.get_string_width(label) + 2
    pdf.cell(lw, 13, label)
    pdf.set_font("liberation", "", 10)
    pdf.multi_cell(W - lw, 13, text, new_x="LMARGIN", new_y="NEXT", align="L")

def bullet(text):
    pdf.set_font("liberation", "", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(10, 13, "-")
    pdf.multi_cell(W - 10, 13, text, new_x="LMARGIN", new_y="NEXT", align="L")

def job(title_org, dates):
    pdf.set_font("liberation", "B", 11)
    pdf.set_text_color(*DARK)
    pdf.cell(W - 130, 14, f"{title_org}")
    pdf.set_font("liberation", "", 10)
    pdf.cell(0, 13, dates, align="R", new_x="LMARGIN", new_y="NEXT")

# Header
h1("PAUL J. ROMEO")
contact_line()

section("Summary")
para("Security-focused IT professional who owns security and IT operations end-to-end for a "
     "multi-channel e-commerce company. Leads incident response and phishing/BEC investigations "
     "through to attacker-infrastructure takedowns; administers ESET EDR, UniFi networking and "
     "Protect surveillance, and TrueNAS storage. B.S. in Cybersecurity & Information Assurance "
     "(WGU, August 2026) backed by nine industry certifications including Security+, CySA+, "
     "PenTest+, and ISC2 SSCP.")

section("Core Skills")
skill_line("Security Operations:",
           "EDR Administration (ESET EDR / Cloud Protect) | Phishing & BEC Investigation | "
           "Attacker-Infrastructure Takedowns | Log Analysis | Wazuh SIEM | Duo MFA | "
           "Vulnerability Management | Endpoint Hardening | Patch Management")
skill_line("Network & Infrastructure:",
           "UniFi Networking | VLANs & Segmentation | TCP/IP, DNS, Wi-Fi | TrueNAS / SMB Storage | "
           "Backup & Disaster Recovery | Windows & Active Directory")
skill_line("Automation & Tools:", "Python | PowerShell | Bash | Git | GitHub Actions CI/CD")
skill_line("Business Platforms:", "BigCommerce | Amazon FBA | eBay | POS Integration")

section("Certifications")
certs = [
    ("CompTIA PenTest+ (PT0-003)", "e3a26d1b0a1944db8e569cfa0ce20432", "Apr 2026 - Apr 2029"),
    ("CompTIA CySA+", "RWEXWLLS9NRE5JE2", "Aug 2025 - Aug 2028"),
    ("ISC2 SSCP", "1123939", "Jul 2025"),
    ("CompTIA Project+", "K1MYZLGS02V415QJ", "Jul 2025"),
    ("LPI Linux Essentials", "LPI000661841", "Aug 2025"),
    ("CompTIA Security+", "2SY3TK06GJ44Q4WQ", "Jul 2024 - Jul 2027"),
    ("CompTIA Network+", "N0BPXTXZFFV4QM3T", "Jun 2024 - Jun 2027"),
    ("CompTIA A+", "G33N7H5ZJERE1F5W", "Jun 2024 - Jun 2027"),
    ("ITIL 4 Foundation", "GR671719240PR", "Dec 2024 - Dec 2027"),
]
pdf.set_font("liberation", "", 9.5)
pdf.set_text_color(*DARK)
for name, cid, dates in certs:
    pdf.cell(10, 12, "-")
    pdf.multi_cell(W - 10, 12, f"{name} \u2014 ID {cid} ({dates})",
                   new_x="LMARGIN", new_y="NEXT", align="L")

section("Professional Experience")
job("Systems Administrator & Security Administrator — Belmont Leather Company",
    "Clifton, NJ | 2021 - Present")
for b in [
    "Own security and IT operations end-to-end as the company's sole internal administrator: workstations, printers, network devices, storage, and backups.",
    "Administer ESET EDR and ESET Cloud Protect across ~15 endpoints; built automated threat alerting, weekly CVE exposure reviews, and endpoint update management.",
    "Lead phishing and BEC incident response end-to-end, filing registrar/host/abuse-desk takedowns against live campaigns (ClickFix malware lures, BEC impersonation attempts, SSA/ScreenConnect lures, and brand-impersonation waves).",
    "Designed and deployed core infrastructure: a UniFi network with VLAN segmentation, a 10-camera UniFi Protect surveillance system, and TrueNAS storage with SMB shares and scheduled cloud backup.",
    "Drove e-commerce growth on BigCommerce integrated with point-of-sale: 389% sales growth and $1.2M in new revenue; cut $12K in costs through POS/e-commerce integration and added $32K/year via customer-relationship systems.",
]:
    bullet(b)
pdf.ln(3)
job("Theater Technician (Part-time) — Rowan University", "2018 - 2020")
bullet("Operated and maintained lighting, sound, and life-safety systems across 20+ live productions, troubleshooting failures under show-time pressure.")
bullet("Coordinated setup and teardown with student and faculty crews for rehearsals, performances, and campus events.")
pdf.ln(3)
job("IT Help Desk Technician & Media Services Specialist — Southern New Hampshire University",
    "2016 - 2018")
bullet("Delivered Tier 1/2 support to 200+ users: malware removal, security policy enforcement, "
       "hardware/software triage, and account administration.")
bullet("Maintained classroom and AV technology across campus, supporting lectures, media playback, "
       "and hybrid events.")

section("Education")
para("B.S. Cybersecurity & Information Assurance — Western Governors University, August 2026", style="B", h=12)
para("Capstone (D833): Wazuh SIEM deployment + Duo MFA proposal — passed on first submission.", size=9)

pdf.output(PDF)
print("pages:", pdf.pages_count)
