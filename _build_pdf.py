#!/usr/bin/env python3
"""
Build the AI-Ready Banking white paper PDFs.
Pipeline: HTML (single source of truth) -> html.parser -> fpdf2 typesetting.
No browser, no external services. Pure Python.

Usage: python _build_pdf.py
"""
import html as htmlmod
import os
import re
import sys
from html.parser import HTMLParser

from fpdf import FPDF
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.abspath(__file__))
WP = os.path.join(ROOT, "white-papers")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

PW, PH = 210, 297  # A4, mm
ML, MR, MT, MB = 18, 18, 20, 22
BODY_W = PW - ML - MR

INK = (16, 27, 40)
NAVY = (13, 27, 42)
GOLD = (143, 97, 24)
GOLD_LT = (200, 164, 92)
MUTE = (95, 109, 122)
RULE = (216, 221, 227)
PAPER_TINT = (240, 237, 230)

# ---------------- papers ----------------

PAPERS = [
    {
        "slug": "core-pillars-of-ai-ready-banking",
        "no": "01",
        "title": "Core Pillars of AI-Ready Banking",
        "cover": ["Core Pillars of", "AI-Ready Banking"],
        "subtitle": "What it takes for a bank to put AI in the decision path: one clean view of the customer, events that arrive in time, and governance the system enforces on itself.",
        "date": "August 2026",
        "subject": "The data, delivery, and governance foundations for AI in a regulated bank.",
    },
    {
        "slug": "strategic-benefits-of-rest-apis-in-open-banking",
        "no": "02",
        "title": "The Strategic Benefits of REST APIs in Open Banking",
        "cover": ["The Strategic Benefits of", "REST APIs in Open Banking"],
        "subtitle": "REST APIs as the foundation of Open Banking: secure, scalable, real-time data exchange that makes Banking-as-a-Service and embedded finance possible.",
        "date": "August 2026",
        "subject": "REST APIs as the strategic foundation of Open Banking, Banking-as-a-Service, and embedded finance.",
    },
    {
        "slug": "future-of-banking-open-banking",
        "no": "03",
        "title": "Future of Banking: Open Banking",
        "cover": ["Future of Banking:", "Open Banking"],
        "subtitle": "Enterprise agility and an API-first architecture as the two critical enablers of Open Banking, with a framework for the transformation journey.",
        "date": "August 2026",
        "subject": "Enterprise agility and API-first architecture as the critical enablers of Open Banking transformation.",
    },
    {
        "slug": "why-cybersecurity-is-important-in-banking",
        "no": "04",
        "title": "Why Cybersecurity is Important in Banking",
        "cover": ["Why Cybersecurity is", "Important in Banking"],
        "subtitle": "How protecting data, payments, and trust became the strategic foundation of a modern bank, from fraud prevention to the resilience of critical infrastructure.",
        "date": "August 2026",
        "subject": "Why cybersecurity is the strategic foundation of digital banking: data protection, fraud prevention, trust, compliance, and operational resilience.",
    },
]


def font_paths():
    """Map fpdf style names to static TTF files (built from the variable fonts)."""
    return {
        "": os.path.join(FONT_DIR, "static", "newsreader-400.ttf"),
        "B": os.path.join(FONT_DIR, "static", "newsreader-600.ttf"),
        "I": os.path.join(FONT_DIR, "static", "newsreader-i400.ttf"),
        "D": os.path.join(FONT_DIR, "static", "newsreader-display.ttf"),
    }


# ---------------- content: parse the HTML ----------------

class PaperParser(HTMLParser):
    """Extract the readable article from a paper HTML file."""

    def __init__(self):
        super().__init__()
        self.blocks = []
        self.open = []
        self.list_stack = None
        self.box_depth = 0
        self.in_article = False

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.in_article = True
            return
        if not self.in_article:
            return
        cls = dict(attrs).get("class", "")
        if tag in ("h2", "h3"):
            b = {"tag": tag, "text": ""}
        elif tag == "p":
            if self.box_depth:
                kind = "boxlabel" if "box-label" in cls else "box"
            elif "lede" in cls:
                kind = "lede"
            elif "box-label" in cls:
                kind = "boxlabel"
            else:
                kind = "p"
            b = {"tag": "p", "text": "", "kind": kind}
        elif tag == "li":
            b = {"tag": "li", "text": ""}
        elif tag in ("ul", "ol"):
            b = {"tag": "list", "ordered": tag == "ol", "items": []}
            self.blocks.append(b)
            self.list_stack = b
            return
        elif tag == "div" and "colophon" in cls:
            b = {"tag": "colophon", "text": ""}
        elif tag == "div" and "box" in cls:
            self.box_depth += 1
            return
        elif tag == "br":
            if self.open:
                self.open[-1]["text"] += " "
            return
        elif tag in ("strong", "b"):
            if self.open:
                self.open[-1]["text"] += "**"
            return
        elif tag in ("em", "i"):
            if self.open:
                self.open[-1]["text"] += "*"
            return
        else:
            return
        self.blocks.append(b)
        self.open.append(b)

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False
            for _ in range(len(self.open)):
                self.open.pop()
            self.list_stack = None
            self.box_depth = 0
            return
        if not self.in_article:
            return
        if tag in ("strong", "b"):
            if self.open:
                self.open[-1]["text"] += "**"
        elif tag in ("em", "i"):
            if self.open:
                self.open[-1]["text"] += "*"
        elif tag == "li":
            if self.open and self.list_stack is not None:
                item = self.open.pop()
                self.list_stack["items"].append(item["text"].strip())
        elif tag in ("h2", "h3", "p"):
            if self.open:
                self.open.pop()
        elif tag == "div":
            if self.open and self.open[-1].get("tag") == "colophon":
                self.open.pop()
            if self.box_depth:
                self.box_depth -= 1
        elif tag in ("ul", "ol"):
            self.list_stack = None

    def handle_data(self, data):
        if self.in_article and self.open:
            self.open[-1]["text"] += data


def clean(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(s)).strip()


def parse(src):
    p = PaperParser()
    p.feed(open(src, encoding="utf-8").read())
    out = []
    for b in p.blocks:
        if b["tag"] in ("h2", "h3"):
            t = clean(b["text"])
            num = ""
            m = re.match(r"^(\d+)\s*", t)
            if m:
                num, t = m.group(1), t[m.end():]
            out.append({"tag": b["tag"], "num": num, "text": t})
        elif b["tag"] == "p":
            out.append({"tag": "p", "kind": b.get("kind", "p"), "text": clean(b["text"])})
        elif b["tag"] == "colophon":
            out.append({"tag": "colophon", "text": clean(b["text"])})
        elif b["tag"] == "list":
            out.append({"tag": "list", "ordered": b["ordered"], "items": [clean(i) for i in b["items"]]})
    return out


# ---------------- the PDF ----------------

class PaperPDF(FPDF):
    def __init__(self):
        super().__init__(format="A4", unit="mm")
        self.compress = True
        self._box_label = ""

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(PH - MB + 4)
        self.set_font("Newsreader", "", 8.5)
        self.set_text_color(*MUTE)
        self.cell(0, 5, str(self.page_no()), align="R")

    def rule(self, thick=0.3):
        self.set_fill_color(*RULE)
        self.rect(ML, self.get_y(), BODY_W, thick, style="F")
        self.ln(0.8)

    def emit(self, blk):
        tag = blk["tag"]
        if tag == "h2":
            if self.get_y() > PH - MB - 42:
                self.add_page()
            self.ln(7)
            self.set_font("Newsreader", "B", 15)
            if blk["num"]:
                self.set_text_color(*GOLD)
                self.set_x(ML)
                self.cell(9, 7, blk["num"], new_x="RIGHT", new_y="TOP")
            self.set_text_color(*INK)
            self.multi_cell(BODY_W - 9, 7, blk["text"], new_x="LEFT", new_y="NEXT")
            self.ln(1.5)
            self.rule()
            self.ln(3.2)
        elif tag == "h3":
            if self.get_y() > PH - MB - 34:
                self.add_page()
            self.ln(4.5)
            self.set_font("Newsreader", "B", 12)
            self.set_text_color(*INK)
            self.multi_cell(BODY_W, 6, blk["text"], new_x="LEFT", new_y="NEXT")
            self.ln(1.8)
        elif tag == "p":
            self.paragraph(blk)
        elif tag == "list":
            self.emit_list(blk)
        elif tag == "colophon":
            self.emit_colophon(blk["text"])

    def paragraph(self, blk):
        kind = blk.get("kind", "p")
        if kind == "lede":
            if self.get_y() > PH - MB - 42:
                self.add_page()
            self.ln(2.5)
            y0 = self.get_y()
            self.set_font("Newsreader", "I", 13)
            self.set_text_color(60, 74, 90)
            self.multi_cell(BODY_W - 8, 7, blk["text"], new_x="LEFT", new_y="NEXT")
            self.set_fill_color(154, 107, 35)
            self.rect(ML - 2, y0, 1.1, self.get_y() - y0, style="F")
            self.ln(3.2)
        elif kind == "p":
            self.set_font("Newsreader", "", 10.5)
            self.set_text_color(*INK)
            self.multi_cell(BODY_W, 5.3, blk["text"], markdown=True, new_x="LEFT", new_y="NEXT")
            self.ln(1.6)
        elif kind == "boxlabel":
            self._box_label = blk["text"]
        elif kind == "box":
            self.emit_box(blk["text"])

    def emit_box(self, body):
        label = self._box_label
        self._box_label = ""
        if self.get_y() > PH - MB - 62:
            self.add_page()
        self.ln(2.5)
        pad = 5
        inner_w = BODY_W - 2 * pad
        y0 = self.get_y() + 1.5
        # measure content
        h_label = 0
        if label:
            self.set_font("Newsreader", "B", 9)
            h_label = self.multi_cell(inner_w, 4.8, label, dry_run=True, output="HEIGHT")
        self.set_font("Newsreader", "", 10.3)
        h_body = self.multi_cell(inner_w, 5.1, body, dry_run=True, output="HEIGHT")
        box_h = 2 + (h_label + 1.2 if label else 0) + h_body + 2
        # paint
        self.set_fill_color(*PAPER_TINT)
        self.set_draw_color(*RULE)
        self.rect(ML, y0, BODY_W, box_h, style="DF")
        yy = y0 + 2
        if label:
            self.set_y(yy)
            self.set_font("Newsreader", "B", 9)
            self.set_text_color(*GOLD)
            self.multi_cell(inner_w, 4.8, label, new_x="LEFT", new_y="NEXT")
            self.ln(1.2)
            yy = self.get_y()
        self.set_y(yy)
        self.set_font("Newsreader", "", 10.3)
        self.set_text_color(*INK)
        self.multi_cell(inner_w, 5.1, body, markdown=True, new_x="LEFT", new_y="NEXT")
        self.set_y(max(self.get_y(), y0 + box_h) + 0.5)
        self.ln(4)

    def emit_list(self, blk):
        ordered, items = blk["ordered"], blk["items"]
        self.ln(0.8)
        for i, item in enumerate(items, 1):
            if self.get_y() > PH - MB - 16:
                self.add_page()
            marker = f"{i}." if ordered else "\u2022"
            self.set_font("Newsreader", "B" if ordered else "", 10.5)
            self.set_text_color(*GOLD)
            self.set_x(ML + 1.5)
            self.cell(9, 5.2, marker, new_x="LEFT", new_y="TOP")
            self.set_font("Newsreader", "", 10.5)
            self.set_text_color(*INK)
            self.set_x(ML + 11)
            self.multi_cell(BODY_W - 11, 5.2, item, markdown=True, new_x="LEFT", new_y="NEXT")
            self.ln(1.3)
        self.ln(1.6)

    def emit_colophon(self, text):
        if text.startswith("About this paper"):
            text = "**About this paper**\n" + text[len("About this paper"):].lstrip()
        self.ln(6)
        self.rule()
        self.ln(2.5)
        self.set_font("Newsreader", "", 9)
        self.set_text_color(*MUTE)
        self.multi_cell(BODY_W, 4.6, text, markdown=True, new_x="LEFT", new_y="NEXT")


def build(paper):
    fonts = font_paths()
    src = os.path.join(WP, paper["slug"] + ".html")
    out = os.path.join(WP, paper["slug"] + ".pdf")

    pdf = PaperPDF()
    pdf.set_title(paper["title"])
    pdf.set_author("AI-Ready Banking Series")
    pdf.set_subject(paper["subject"])

    pdf.add_font("Newsreader", "", fonts[""])
    pdf.add_font("Newsreader", "B", fonts["B"])
    pdf.add_font("Newsreader", "I", fonts["I"])
    pdf.add_font("NewsreaderD", "B", fonts["D"])

    # ---- cover ----
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, PW, PH, style="F")
    pdf.set_xy(24, 34)
    pdf.set_font("Newsreader", "", 11)
    pdf.set_char_spacing(1.6)
    pdf.set_text_color(*GOLD_LT)
    pdf.cell(0, 6, "WHITE PAPER  \u00b7  NO. " + paper["no"])
    pdf.set_char_spacing(0)
    pdf.set_xy(24, 50)
    pdf.set_font("NewsreaderD", "B", 26)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(155, 13.5, "\n".join(paper["cover"]), new_x="LEFT", new_y="NEXT")
    pdf.set_xy(24, 98)
    pdf.set_font("Newsreader", "", 12.5)
    pdf.set_text_color(185, 199, 217)
    pdf.multi_cell(128, 7.5, paper["subtitle"], new_x="LEFT", new_y="NEXT")
    pdf.set_draw_color(255, 255, 255)
    pdf.line(24, PH - 46, PW - 24, PH - 46)
    pdf.set_xy(24, PH - 39)
    pdf.set_font("Newsreader", "", 9.5)
    pdf.set_text_color(147, 165, 187)
    pdf.cell(80, 6, "AI-Ready Banking Series")
    pdf.set_xy(PW - 24 - 45, PH - 39)
    pdf.cell(45, 6, paper["date"], align="R")

    # ---- content ----
    pdf.set_margins(ML, MT, MR)
    pdf.set_auto_page_break(auto=True, margin=MB + 6)
    pdf.add_page()
    for blk in parse(src):
        pdf.emit(blk)

    pdf.output(out)
    return out, os.path.getsize(out), pdf.pages_count


if __name__ == "__main__":
    only = sys.argv[1:] or None
    for paper in PAPERS:
        if only and paper["slug"] not in only:
            continue
        src = os.path.join(WP, paper["slug"] + ".html")
        if not os.path.exists(src):
            print("missing source:", src)
            continue
        out, size, pages = build(paper)
        print(f"wrote {out} | {size} bytes | {pages} pages | No. {paper['no']}")