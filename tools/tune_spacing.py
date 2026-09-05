"""Post-build: strip Word's default paragraph spacing so the .docx
layout matches the fpdf-generated PDF (single-spaced, no gaps).
"""
from docx import Document
from docx.shared import Pt

doc = Document("Paul-Romeo-Resume.docx")

names = ["Normal", "Body", "ContactLine", "SectionHeader", "JobTitle",
         "JobMeta", "List Bullet", "List Paragraph"]
styles = [doc.styles[name] for name in names if name in doc.styles]
for item in [*styles, *doc.paragraphs]:
    pf = item.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0

doc.save("Paul-Romeo-Resume.docx")
print("spacing stripped")
