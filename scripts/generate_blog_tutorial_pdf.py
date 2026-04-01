from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "blog-web-app-tutorial.md"
OUTPUT_DIR = ROOT / "src" / "main" / "resources" / "static" / "docs"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip()).strip("-").lower()
    return value or "document"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#102a43"),
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#486581"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0b7285"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1f3c88"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13.5,
            textColor=colors.HexColor("#102a43"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.2,
            leftIndent=12,
            firstLineIndent=-8,
            bulletIndent=0,
            textColor=colors.HexColor("#102a43"),
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            fontName="Courier",
            fontSize=7.2,
            leading=8.8,
            textColor=colors.HexColor("#102a43"),
            backColor=colors.HexColor("#f1f5f9"),
            borderColor=colors.HexColor("#d9e2ec"),
            borderWidth=0.6,
            borderPadding=6,
            leftIndent=6,
            rightIndent=6,
            spaceBefore=4,
            spaceAfter=8,
        )
    )
    return styles


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, width, height, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#d9e2ec"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, height - 1.8 * cm, width - 2 * cm, height - 1.8 * cm)
    canvas.line(2 * cm, 1.5 * cm, width - 2 * cm, 1.5 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#486581"))
    canvas.drawString(2 * cm, height - 1.4 * cm, "Spring Boot MVC Blog Tutorial")
    canvas.drawRightString(width - 2 * cm, 1.05 * cm, f"Page {doc.page}")
    canvas.restoreState()


def architecture_diagram():
    return Preformatted(
        textwrap.dedent(
            """\
            +-------------------+       +-------------------+       +-------------------+
            |   Browser/User    | ----> |   Controllers     | ----> |     Services      |
            +-------------------+       +-------------------+       +-------------------+
                                                                              |
                                                                              v
                                                                   +-------------------+
                                                                   |   Repositories    |
                                                                   +-------------------+
                                                                              |
                                                                              v
                                                                   +-------------------+
                                                                   |      MySQL        |
                                                                   +-------------------+
            """
        ),
        style=STYLES["CodeBlock"],
    )


def verification_diagram():
    return Preformatted(
        textwrap.dedent(
            """\
            Register Form
                 |
                 v
            Validate Inputs
                 |
                 v
            Save User (enabled=false)
                 |
                 v
            Create Verification Token
                 |
                 v
            Send Email Link
                 |
                 v
            User Clicks /verify?token=...
                 |
                 v
            Validate Token -> Enable User -> Allow Login
            """
        ),
        style=STYLES["CodeBlock"],
    )


def parse_markdown(lines):
    story = []
    in_code = False
    code_lines: list[str] = []

    for raw in lines:
        line = raw.rstrip("\n")

        if line.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), STYLES["CodeBlock"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            story.append(Spacer(1, 0.12 * cm))
            continue

        if line.startswith("# "):
            story.append(Paragraph(line[2:].strip(), STYLES["DocTitle"]))
            generated = datetime.now().strftime("%Y-%m-%d %H:%M")
            story.append(
                Paragraph(
                    f"Generated on {generated} | Spring Boot, Thymeleaf, Bootstrap 5, Spring Security, MySQL",
                    STYLES["DocSubtitle"],
                )
            )
            story.append(architecture_diagram())
            story.append(verification_diagram())
            continue

        if line.startswith("## "):
            heading = line[3:].strip()
            if story:
                story.append(Spacer(1, 0.15 * cm))
            story.append(Paragraph(heading, STYLES["Section"]))
            continue

        if line.startswith("### "):
            story.append(Paragraph(line[4:].strip(), STYLES["SubSection"]))
            continue

        if line.startswith("- "):
            story.append(Paragraph(line[2:].strip(), STYLES["BulletBody"], bulletText="•"))
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", line)
        if numbered:
            story.append(Paragraph(numbered.group(2), STYLES["BulletBody"], bulletText=f"{numbered.group(1)}."))
            continue

        story.append(Paragraph(format_inline_code(line), STYLES["Body"]))

    return compress_spacers(story)


def format_inline_code(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    converted = []
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            code = escape_xml(part[1:-1])
            converted.append(f'<font name="Courier">{code}</font>')
        else:
            converted.append(escape_xml(part))
    return "".join(converted)


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def compress_spacers(story):
    cleaned = []
    previous_spacer = False
    for item in story:
        is_spacer = isinstance(item, Spacer)
        if is_spacer and previous_spacer:
            continue
        cleaned.append(item)
        previous_spacer = is_spacer
    return cleaned


def build_pdf(output_path: Path):
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        title="Blog Web Application Tutorial",
        author="Codex",
    )

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    template = PageTemplate(id="blog-tutorial", frames=[frame], onPage=draw_page)
    doc.addPageTemplates([template])

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story = parse_markdown(lines)
    wrapped_story = [KeepTogether([item]) if isinstance(item, Preformatted) else item for item in story]
    doc.build(wrapped_story)


if __name__ == "__main__":
    STYLES = build_styles()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_name = f"{timestamp}-blog-web-application-tutorial.pdf"
    build_pdf(OUTPUT_DIR / output_name)
    print(output_name)
