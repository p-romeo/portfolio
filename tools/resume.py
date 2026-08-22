"""Generate Paul Romeo's one-page ATS-friendly resume PDF (fpdf2)."""
from fpdf import FPDF

PDF = "Paul-Romeo-Resume.pdf"

pdf = FPDF(format="letter", unit="pt")
pdf.set_auto_page_break(auto=False)
pdf.set_margins(40, 36, 40)
pdf.add_page()
W = pdf.w - 80  # usable width

DARK = (25, 30, 38)
ACCENT = (30, 70, 120)

def h1(text):
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 22, text, align="C", new_x="LMARGIN", new_y="NEXT")

def contact_line():
    pdf.set_font("helvetica", "", 9.5)
    pdf.set_text_color(70, 78, 90)
    pdf.cell(0, 13, "pauljromeo@proton.me  |  Union, NJ  |  linkedin.com/in/paul-romeo",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

def section(title):
    y = pdf.get_y() + 2
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 14, title.upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.7)
    pdf.line(40, y + 13, 40 + W, y + 13)
    pdf.ln(3)

def para(text, size=9.5, style="", h=12):
    pdf.set_font("helvetica", style, size)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(W, h, text, new_x="LMARGIN", new_y="NEXT")

def bullet(text):
    pdf.set_font("helvetica", "", 9.5)
    pdf.set_text_color(*DARK)
    x = pdf.get_x()
    pdf.cell(10, 12, "-")
    pdf.multi_cell(W - 10, 12, text, new_x="LMARGIN", new_y="NEXT")

def job(title_org, dates, location=None):
    pdf.set_font("helvetica", "B", 10.5)
    pdf.set_text_color(*DARK)
    pdf.cell(W - 130, 13, f"{title_org}")
    pdf.set_font("helvetica", "", 9.5)
    txt = dates if not location else f"{location} | {dates}"
    pdf.cell(0, 13, txt, align="R", new_x="LMARGIN", new_y="NEXT")

# Header
h1("PAUL J ROMEO")
contact_line()

section("Summary")
para("Security-focused IT professional running security and IT end-to-end for a multi-channel "
     "e-commerce company: EDR, network defense, and incident response with attacker-infrastructure "
     "takedowns. B.S. Cybersecurity & Information Assurance (WGU, August 2026). Hands-on experience "
     "with phishing/BEC investigation, abuse-desk takedowns, ESET EDR administration, UniFi/Protect, "
     "and TrueNAS.")

section("Certifications")
certs = [
    ("CompTIA PenTest+ (PT0-003)", "e3a26d1b0a1944db8e569cfa0ce20432", "Apr 2026 - Apr 2029"),
    ("CompTIA CySA+", "RWEXWLLS9NRE5JE2", "Aug 2025 - Aug 2028"),
    ("CompTIA Security+", "2SY3TK06GJ44Q4WQ", "Jul 2024 - Jul 2027"),
    ("CompTIA Network+", "N0BPXTXZFFV4QM3T", "Jun 2024 - Jun 2027"),
    ("CompTIA A+", "G33N7H5ZJERE1F5W", "Jun 2024 - Jun 2027"),
    ("CompTIA Project+", "K1MYZLGS02V415QJ", "Jul 2025"),
    ("ISC2 SSCP", "1123939", "Jul 2025"),
    ("ITIL 4 Foundation", "GR671719240PR", "Dec 2024 - Dec 2027"),
    ("LPI Linux Essentials", "LPI000661841", "Aug 2025"),
]
for name, cid, dates in certs:
    bullet(f"{name} -- ID {cid} ({dates})")

section("Experience")
job("Belmont Leather Company -- Systems Administrator & Security Administrator",
    "Clifton, NJ | 2021 - Present")
for b in [
    "Sole internal IT administrator: workstations, printers, storage, backups, network devices.",
    "Administer ESET EDR + ESET Cloud Protect (~15 endpoints): automated threat alerting, weekly CVE exposure review, endpoint update management.",
    "Investigate phishing and BEC attacks; perform attacker-infrastructure takedowns via registrar/host/abuse-desk reports (cases include a ClickFix campaign, a BEC impersonation attempt, an SSA/ScreenConnect lure, and brand-impersonation waves).",
    "Installed and configured UniFi network plus a 10-camera UniFi Protect surveillance system.",
    "Implemented TrueNAS storage server with SMB shares and scheduled cloud backup.",
    "Scaled BigCommerce platform integrated with POS: 389% sales growth, $1.2M new revenue, $12K costs cut via POS/e-commerce integration, +$32K/year from customer relationship systems.",
]:
    bullet(b)
pdf.ln(3)
job("Rowan University -- Theater Technician (Part-time)", "2018 - 2019")
bullet("Lighting, sound, and safety systems for 20+ productions.")
pdf.ln(3)
job("Southern New Hampshire University -- IT Help Desk Technician & Media Services Specialist",
    "2016 - 2018")
bullet("Tier 1/2 support for 200+ users, malware removal, security policy enforcement, classroom technology maintenance.")

section("Projects")
bullet("Signal Vault (github.com/p-romeo/signal-vault) -- open-source scam/phishing triage engine, TypeScript/React, 15+ detectors, 60 tests. Built from real IR casework.")
bullet("ctf-toolkit (github.com/p-romeo/ctf-toolkit) -- Python CTF tool suite with crypto tools covered by a pytest known-vector test suite.")

section("Skills")
para("ESET EDR administration | ESET Cloud Protect | Windows & Active Directory | endpoint hardening | "
     "vulnerability management | patch pipelines | backup & disaster recovery | phishing/BEC investigation | "
     "infrastructure takedowns | log analysis | Wazuh SIEM | Duo MFA | UniFi networking | UniFi Protect | "
     "TrueNAS/SMB | TCP/IP | DNS | VLANs | Wi-Fi | segmentation | Bash | Python | PowerShell | Git | "
     "GitHub Actions CI/CD | BigCommerce/Amazon/eBay platforms")

section("Education")
para("B.S. Cybersecurity & Information Assurance -- Western Governors University, August 2026", style="B", h=12)
para("Capstone (D833): Wazuh SIEM deployment + Duo MFA proposal -- passed on first submission.", size=9)

pdf.output(PDF)
print("pages:", pdf.pages_count)
