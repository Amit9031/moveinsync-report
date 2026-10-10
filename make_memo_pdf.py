"""Turn MEMO.md into MEMO.pdf. Edit MEMO.md, then run:  python make_memo_pdf.py
Needs: pip install reportlab"""
import re, sys
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, KeepTogether

src = sys.argv[1] if len(sys.argv) > 1 else "MEMO.md"
out = sys.argv[2] if len(sys.argv) > 2 else "MEMO.pdf"
INK, ACC, LINE = colors.HexColor("#17252e"), colors.HexColor("#0b6e6e"), colors.HexColor("#cfd6d2")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica", fontSize=9.6, leading=13.2, textColor=INK, spaceAfter=4)
small = ParagraphStyle("s", parent=body, fontSize=8.4, leading=11)
h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=18, leading=22, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=ACC, spaceBefore=10, spaceAfter=4)
cell = ParagraphStyle("c", parent=body, fontSize=8.4, leading=10.6, spaceAfter=0)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold")

def inline(t):
    t = t.replace("\u2605", "-star").replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", " - ")
    t = re.sub(r"(\d)-star", r"\1-star", t)
    t = escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', t)
    t = re.sub(r"\[FILL[^\]]*\]", lambda m: f'<font backColor="#ffe46b">{m.group(0)}</font>', t)
    return t

def table(rows):
    rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows if not re.match(r"^\s*\|[\s:|-]+\|\s*$", r)]
    n = len(rows[0]); data = []
    for i, r in enumerate(rows):
        r += [""] * (n - len(r))
        data.append([Paragraph(inline(c), cellb if i == 0 else cell) for c in r])
    w = [min(max(max(len(r[j]) for r in rows), 8), 55) for j in range(n)]
    total = A4[0] - 36 * mm
    t = Table(data, colWidths=[total * x / sum(w) for x in w], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6efed")), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]))
    return t

story, lines, i = [], open(src, encoding="utf-8").read().splitlines(), 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("# "): story.append(Paragraph(inline(ln[2:]), h1))
    elif ln.startswith("## "): story.append(Paragraph(inline(ln[3:]), h2))
    elif ln.startswith("|"):
        blk = []
        while i < len(lines) and lines[i].startswith("|"): blk.append(lines[i]); i += 1
        story += [table(blk), Spacer(1, 6)]; continue
    elif ln.startswith("- "):
        items = []
        while i < len(lines) and lines[i].startswith("- "): items.append(ListItem(Paragraph(inline(lines[i][2:]), body), leftIndent=12)); i += 1
        story.append(ListFlowable(items, bulletType="bullet", start="\u2022", leftIndent=12, bulletFontSize=8)); continue
    elif ln.strip(): story.append(Paragraph(inline(ln), small if ln.startswith("Note:") else body))
    i += 1

def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 7.5); c.setFillColor(colors.grey)
    c.drawString(18 * mm, 10 * mm, "MoveInSync Play Store rating: recommendation"); c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {d.page}"); c.restoreState()

SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                  title="Raising MoveInSync's Play Store rating", author="").build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", out)
