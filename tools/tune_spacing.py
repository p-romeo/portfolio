"""Post-build: strip Word's default paragraph spacing so the .docx
layout matches the fpdf-generated PDF (single-spaced, no gaps).
"""
from docx import Document
from docx.shared import Pt

doc = Document("Paul-Romeo-Resume.docx")

# Kill spacing at the style level (covers every paragraph using these styles)
for name in ["Normal", "Body", "ContactLine", "SectionHeader", "JobTitle",
             "JobMeta", "List Bullet", "List Paragraph"]:
    try:
        st = doc.styles[name]
    except KeyError:
        continue
    pf = st.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0

# Belt-and-suspenders: also force it on every actual paragraph
for p in doc.paragraphs:
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0

doc.save("Paul-Romeo-Resume.docx")
print("spacing stripped")
