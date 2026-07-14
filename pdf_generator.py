from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#082B63")
DARK_NAVY = colors.HexColor("#071C3A")
ORANGE = colors.HexColor("#F97316")
SLATE = colors.HexColor("#475569")
LIGHT_BLUE = colors.HexColor("#EFF6FF")
LIGHT_ORANGE = colors.HexColor("#FFF7ED")
LIGHT_GRAY = colors.HexColor("#F8FAFC")
MID_GRAY = colors.HexColor("#E5E7EB")
WHITE = colors.white


def safe_text(value):
    """Escape text for ReportLab Paragraph markup and preserve line breaks."""
    if value is None:
        return ""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def severity_color(severity):
    severity = str(severity).lower()

    if severity == "high":
        return colors.HexColor("#FEE2E2")

    if severity == "medium":
        return colors.HexColor("#FEF3C7")

    if severity == "low":
        return colors.HexColor("#DCFCE7")

    return colors.HexColor("#F1F5F9")


def _card_style(background=WHITE, border=MID_GRAY, left_border=None):
    commands = [
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.6, border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]

    if left_border:
        commands.append(("LINEBEFORE", (0, 0), (0, -1), 4, left_border))

    return TableStyle(commands)


def build_pdf(
    brief: dict,
    clarifier_output: str = "",
    skeptic_output: str = "",
    methodologist_output: str = "",
) -> bytes:
    """Build a polished Crucible Review PDF.

    The three agent outputs are optional so existing calls such as
    build_pdf(brief) still work.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="The Crucible Review",
        author="The Crucible Review",
    )

    base_styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=base_styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=27,
        alignment=TA_CENTER,
        textColor=DARK_NAVY,
        spaceAfter=7,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=SLATE,
        spaceAfter=16,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=DARK_NAVY,
        spaceBefore=13,
        spaceAfter=8,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=base_styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1F2937"),
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=base_styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
    )

    label_style = ParagraphStyle(
        "LabelStyle",
        parent=small_style,
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=NAVY,
        spaceAfter=3,
    )

    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=base_styles["Normal"],
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
    )

    story = []

    # Cover/header
    story.append(Paragraph("THE CRUCIBLE REVIEW", title_style))
    story.append(
        Paragraph(
            "Ideas strengthened through structured challenge.",
            subtitle_style,
        )
    )

    domain = safe_text(brief.get("domain", "Other"))
    generated_date = datetime.now().strftime("%B %d, %Y")

    metadata_table = Table(
        [
            [
                Paragraph("<b>DOMAIN</b><br/>" + domain, small_style),
                Paragraph("<b>GENERATED</b><br/>" + generated_date, small_style),
                Paragraph("<b>REPORT TYPE</b><br/>Executive Challenge Brief", small_style),
            ]
        ],
        colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch],
    )
    metadata_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                ("BOX", (0, 0), (-1, -1), 0.6, MID_GRAY),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, MID_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(metadata_table)
    story.append(Spacer(1, 8))

    # Executive summary
    story.append(Paragraph("Executive Summary", section_style))
    story.append(
        Table(
            [[Paragraph(safe_text(brief.get("executive_summary", "")), body_style)]],
            colWidths=[7.2 * inch],
            style=_card_style(LIGHT_GRAY, NAVY, NAVY),
        )
    )

    story.append(Paragraph("Idea Under Test", section_style))
    story.append(
        Table(
            [[Paragraph(safe_text(brief.get("idea_under_test", "")), body_style)]],
            colWidths=[7.2 * inch],
            style=_card_style(LIGHT_BLUE, colors.HexColor("#BFDBFE"), NAVY),
        )
    )

    story.append(Paragraph("Working Hypothesis", section_style))
    story.append(
        Table(
            [[Paragraph(safe_text(brief.get("hypothesis", "")), body_style)]],
            colWidths=[7.2 * inch],
            style=_card_style(WHITE, MID_GRAY, ORANGE),
        )
    )

    # Assumptions
    story.append(Paragraph("Assumption Map", section_style))

    assumption_rows = [
        [
            Paragraph("<b>Assumption</b>", small_style),
            Paragraph("<b>Why it matters</b>", small_style),
            Paragraph("<b>How to test</b>", small_style),
        ]
    ]

    for index, item in enumerate(brief.get("assumptions", []), start=1):
        assumption_rows.append(
            [
                Paragraph(
                    f"<b>{index}. {safe_text(item.get('title', ''))}</b>",
                    small_style,
                ),
                Paragraph(safe_text(item.get("why", "")), small_style),
                Paragraph(safe_text(item.get("test", "")), small_style),
            ]
        )

    assumption_table = Table(
        assumption_rows,
        colWidths=[1.9 * inch, 2.55 * inch, 2.75 * inch],
        repeatRows=1,
    )
    assumption_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
                ("GRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(assumption_table)

    # Risks
    story.append(Paragraph("Risk Radar", section_style))

    risk_rows = [
        [
            Paragraph("<b>Severity</b>", small_style),
            Paragraph("<b>Risk</b>", small_style),
            Paragraph("<b>Why it matters</b>", small_style),
        ]
    ]
    risk_backgrounds = []

    for row_index, risk in enumerate(brief.get("risks", []), start=1):
        severity = safe_text(risk.get("severity", "Medium"))
        risk_rows.append(
            [
                Paragraph(f"<b>{severity}</b>", small_style),
                Paragraph(safe_text(risk.get("title", "")), small_style),
                Paragraph(safe_text(risk.get("why", "")), small_style),
            ]
        )
        risk_backgrounds.append((row_index, severity_color(severity)))

    risk_table = Table(
        risk_rows,
        colWidths=[1.0 * inch, 2.4 * inch, 3.8 * inch],
        repeatRows=1,
    )

    risk_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]

    for row_index, background in risk_backgrounds:
        risk_commands.append(
            ("BACKGROUND", (0, row_index), (-1, row_index), background)
        )

    risk_table.setStyle(TableStyle(risk_commands))
    story.append(risk_table)

    # Evidence
    story.append(Paragraph("Critical Evidence", section_style))

    evidence_items = brief.get("evidence_needed", [])
    evidence_rows = []

    for index in range(0, len(evidence_items), 2):
        left = evidence_items[index]
        right = evidence_items[index + 1] if index + 1 < len(evidence_items) else ""

        evidence_rows.append(
            [
                Paragraph(f"&#9633; {safe_text(left)}", small_style),
                Paragraph(f"&#9633; {safe_text(right)}", small_style),
            ]
        )

    if evidence_rows:
        evidence_table = Table(
            evidence_rows,
            colWidths=[3.55 * inch, 3.55 * inch],
        )
        evidence_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                    ("BOX", (0, 0), (-1, -1), 0.4, MID_GRAY),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, MID_GRAY),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.append(evidence_table)

    # Minimum viable investigation
    story.append(Paragraph("Minimum Viable Investigation", section_style))

    test = brief.get("minimum_test", {}) or {}
    mvi_rows = [
        [
            Paragraph("<b>Sample</b>", small_style),
            Paragraph(safe_text(test.get("sample", "")), small_style),
        ],
        [
            Paragraph("<b>Method</b>", small_style),
            Paragraph(safe_text(test.get("method", "")), small_style),
        ],
        [
            Paragraph("<b>Output</b>", small_style),
            Paragraph(safe_text(test.get("output", "")), small_style),
        ],
        [
            Paragraph("<b>Decision</b>", small_style),
            Paragraph(safe_text(test.get("decision", "")), small_style),
        ],
    ]

    mvi_table = Table(
        mvi_rows,
        colWidths=[1.2 * inch, 6.0 * inch],
    )
    mvi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
                ("BACKGROUND", (1, 0), (1, -1), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(mvi_table)

    # Actions
    story.append(Paragraph("Recommended Actions", section_style))

    for index, move in enumerate(brief.get("next_moves", []), start=1):
        action = Table(
            [[Paragraph(f"<b>{index}.</b> {safe_text(move)}", body_style)]],
            colWidths=[7.2 * inch],
            style=_card_style(LIGHT_GRAY, MID_GRAY, NAVY),
        )
        story.append(action)
        story.append(Spacer(1, 4))

    # Challenge cards
    story.append(Paragraph("Challenge Cards", section_style))

    for index, question in enumerate(brief.get("mentor_questions", []), start=1):
        challenge = Table(
            [[Paragraph(f"<b>Challenge {index}:</b> {safe_text(question)}", body_style)]],
            colWidths=[7.2 * inch],
            style=_card_style(LIGHT_ORANGE, colors.HexColor("#FED7AA"), ORANGE),
        )
        story.append(challenge)
        story.append(Spacer(1, 4))

    # Verdict
    recommendation = (
        brief.get("recommendation")
        or brief.get("verdict")
        or brief.get("final_recommendation")
        or (
            "Proceed only after the most consequential assumptions have been "
            "tested with a small, measurable investigation."
        )
    )

    story.append(Paragraph("The Crucible Verdict", section_style))
    story.append(
        Table(
            [[Paragraph(safe_text(recommendation), body_style)]],
            colWidths=[7.2 * inch],
            style=_card_style(LIGHT_ORANGE, ORANGE, ORANGE),
        )
    )

    # Behind the analysis
    analysis_sections = [
        ("Clarifier", clarifier_output),
        ("Skeptic", skeptic_output),
        ("Methodologist", methodologist_output),
    ]

    if any(output.strip() for _, output in analysis_sections):
        story.append(PageBreak())
        story.append(Paragraph("Behind the Analysis", title_style))
        story.append(
            Paragraph(
                "The complete agent perspectives that informed the final brief.",
                subtitle_style,
            )
        )

        for heading, content in analysis_sections:
            if not content.strip():
                continue

            analysis_block = [
                Paragraph(heading, section_style),
                Table(
                    [[Paragraph(safe_text(content), body_style)]],
                    colWidths=[7.2 * inch],
                    style=_card_style(WHITE, MID_GRAY, NAVY),
                ),
                Spacer(1, 8),
            ]
            story.append(KeepTogether(analysis_block))

    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            "Generated by The Crucible Review - an adversarial thinking partner. "
            "This brief supports inquiry and does not replace expert judgment.",
            footer_style,
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf