"""Generate Paul Romeo's one-page ATS-friendly resume PDF (fpdf2).

Content comes from tools/resume_spec.json (shared with the .docx version).
"""
import json
from pathlib import Path

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

def contact_line(text):
    pdf.set_font("liberation", "", 10)
    pdf.set_text_color(70, 78, 90)
    pdf.cell(0, 13, text,
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

with Path(__file__).with_name("resume_spec.json").open(encoding="utf-8") as source:
    blocks = iter(json.load(source)["blocks"])
current_section = ""
job_seen = False
for block in blocks:
    style = block.get("style")
    text = block.get("text", "".join(run["text"] for run in block.get("runs", [])))
    if style == "NameTitle":
        h1(text)
    elif style == "ContactLine":
        contact_line(text)
    elif style == "SectionHeader":
        current_section = text
        section(text)
    elif style == "JobTitle":
        if job_seen:
            pdf.ln(3)
        job_seen = True
        meta = next(blocks)
        assert meta["style"] == "JobMeta", "Job title must be followed by dates"
        job(text, meta["text"])
    elif block["type"] == "bullet_list":
        for item in block["items"]:
            if current_section == "CERTIFICATIONS":
                pdf.set_font("liberation", "", 9.5)
                pdf.set_text_color(*DARK)
                pdf.cell(10, 12, "-")
                pdf.multi_cell(W - 10, 12, item, new_x="LMARGIN", new_y="NEXT", align="L")
            else:
                bullet(item)
    elif current_section == "CORE SKILLS":
        label, value = block["runs"]
        skill_line(label["text"].rstrip(), value["text"])
    elif current_section == "EDUCATION":
        if style == "JobMeta":
            para(text, size=9)
        else:
            para(text, style="B", h=12)
    else:
        para(text)

pdf.output(PDF)
print("pages:", pdf.pages_count)
