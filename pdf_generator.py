from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def safe_text(value):
    if value is None:
        return ""
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def severity_color(severity):
    severity = str(severity).lower()

    if severity == "high":
        return colors.HexColor("#FFE0E0")

    if severity == "medium":
        return colors.HexColor("#FFF1CC")

    if severity == "low":
        return colors.HexColor("#E4F8E4")

    return colors.HexColor("#EEEEEE")


def build_pdf(brief: dict) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    base_styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=base_styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#222222"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=base_styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#222222"),
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=base_styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#333333"),
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=base_styles["BodyText"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#555555"),
    )

    card_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F7F7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]
    )

    story = []

    story.append(Paragraph("Crucible Brief", title_style))
    story.append(
        Paragraph(
            "Clarify assumptions. Challenge conclusions. Design better investigations.",
            subtitle_style,
        )
    )

    domain = safe_text(brief.get("domain", "Other"))

    story.append(
        Table(
            [[Paragraph(f"<b>Domain:</b> {domain}", body_style)]],
            colWidths=[7.2 * inch],
            style=card_style,
        )
    )

    story.append(Spacer(1, 10))

    story.append(Paragraph("Idea Under Test", section_style))
    story.append(
        Table(
            [[Paragraph(safe_text(brief.get("idea_under_test", "")), body_style)]],
            colWidths=[7.2 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF3FF")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFD7F5")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        )
    )

    story.append(Paragraph("Working Hypothesis", section_style))
    story.append(
        Table(
            [[Paragraph(safe_text(brief.get("hypothesis", "")), body_style)]],
            colWidths=[7.2 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF8EA")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8DEB8")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        )
    )

    story.append(Paragraph("Assumption Map", section_style))

    assumption_rows = [[
        Paragraph("<b>Assumption</b>", small_style),
        Paragraph("<b>Why it matters</b>", small_style),
        Paragraph("<b>How to test</b>", small_style),
    ]]

    for item in brief.get("assumptions", []):
        assumption_rows.append(
            [
                Paragraph(safe_text(item.get("title", "")), small_style),
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
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFEFEF")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(assumption_table)

    story.append(Paragraph("Risk Radar", section_style))

    risk_rows = [[
        Paragraph("<b>Severity</b>", small_style),
        Paragraph("<b>Risk</b>", small_style),
        Paragraph("<b>Why</b>", small_style),
    ]]

    risk_backgrounds = []

    for idx, risk in enumerate(brief.get("risks", []), start=1):
        severity = safe_text(risk.get("severity", "Medium"))
        risk_rows.append(
            [
                Paragraph(f"<b>{severity}</b>", small_style),
                Paragraph(safe_text(risk.get("title", "")), small_style),
                Paragraph(safe_text(risk.get("why", "")), small_style),
            ]
        )
        risk_backgrounds.append((idx, severity_color(severity)))

    risk_table = Table(
        risk_rows,
        colWidths=[1.0 * inch, 2.4 * inch, 3.8 * inch],
        repeatRows=1,
    )

    risk_style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFEFEF")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]

    for row_index, bg_color in risk_backgrounds:
        risk_style_commands.append(("BACKGROUND", (0, row_index), (-1, row_index), bg_color))

    risk_table.setStyle(TableStyle(risk_style_commands))
    story.append(risk_table)

    story.append(Paragraph("Evidence Needed", section_style))

    evidence_items = brief.get("evidence_needed", [])
    evidence_rows = []

    for i in range(0, len(evidence_items), 2):
        left = evidence_items[i]
        right = evidence_items[i + 1] if i + 1 < len(evidence_items) else ""

        evidence_rows.append(
            [
                Paragraph(f"&#10003; {safe_text(left)}", small_style),
                Paragraph(f"&#10003; {safe_text(right)}", small_style),
            ]
        )

    evidence_table = Table(
        evidence_rows,
        colWidths=[3.55 * inch, 3.55 * inch],
    )

    evidence_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#EEEEEE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(evidence_table)

    story.append(Paragraph("Minimum Viable Investigation", section_style))

    test = brief.get("minimum_test", {})

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
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFEFEF")),
                ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#FFFFFF")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(mvi_table)

    story.append(Paragraph("Next 3 Moves", section_style))

    for i, move in enumerate(brief.get("next_moves", []), start=1):
        story.append(
            Table(
                [[Paragraph(f"<b>{i}.</b> {safe_text(move)}", body_style)]],
                colWidths=[7.2 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F7F7")),
                        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                ),
            )
        )
        story.append(Spacer(1, 4))

    story.append(Paragraph("Mentor Questions", section_style))

    for question in brief.get("mentor_questions", []):
        story.append(
            Table(
                [[Paragraph(f"? {safe_text(question)}", body_style)]],
                colWidths=[7.2 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8E6")),
                        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#F0D48A")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                ),
            )
        )
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 14))

    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=base_styles["Normal"],
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#777777"),
    )

    story.append(
        Paragraph(
            "Generated by The Crucible Review - an adversarial thinking partner. This brief supports inquiry and does not replace expert judgment.",
            footer_style,
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf