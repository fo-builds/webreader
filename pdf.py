"""Render plain text into a simple PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def make_pdf(title, text, out_path):
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=15)
    doc = SimpleDocTemplate(out_path, pagesize=A4, title=title[:100] or "Web page")
    story = []
    if title:
        story.append(Paragraph(title[:300], styles["Title"]))
        story.append(Spacer(1, 12))
    for para in (text or "").split("\n"):
        para = para.strip()
        if not para:
            continue
        import html
        story.append(Paragraph(html.escape(para[:4000]).replace("\t", "    "), body))
    doc.build(story)
    return out_path
