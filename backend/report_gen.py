
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as ReportImage,
    PageBreak,
)


def safe_text(value):
    """Safely convert values into text that ReportLab can display."""
    if value is None:
        return "Not available"
    return escape(str(value))


def add_visualization(story, label, result, styles):
    """Add an analysis visualization when its image exists."""
    if not isinstance(result, dict):
        return

    image_path = result.get("output_path")

    if image_path and Path(image_path).is_file():
        story.append(Paragraph(safe_text(label), styles["Heading3"]))

        report_image = ReportImage(
            str(image_path),
            width=4.8 * inch,
            height=3.2 * inch,
            kind="proportional",
        )

        story.append(report_image)
        story.append(Spacer(1, 12))


def generate_pdf_report(
    filename: str,
    metadata: dict,
    ela: dict,
    noise: dict,
    edges: dict,
    copy_move: dict,
    evidence: dict,
    output_path: str,
    typography: dict | None = None,
    risk_score: dict | None = None,
) -> str:
    """
    Generate a detailed VerifEye forensic analysis PDF.

    typography and risk_score are optional to preserve compatibility
    with existing calls to this function.
    """

    metadata = metadata if isinstance(metadata, dict) else {}
    ela = ela if isinstance(ela, dict) else {}
    noise = noise if isinstance(noise, dict) else {}
    edges = edges if isinstance(edges, dict) else {}
    copy_move = copy_move if isinstance(copy_move, dict) else {}
    evidence = evidence if isinstance(evidence, dict) else {}
    typography = typography if isinstance(typography, dict) else {}
    risk_score = risk_score if isinstance(risk_score, dict) else {}

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "VerifEyeTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#163A70"),
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#163A70"),
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = styles["BodyText"]

    story = []

    # ---------------------------------------------------------
    # 1. Report header
    # ---------------------------------------------------------
    story.append(Paragraph("VERIFEYE", title_style))
    story.append(
        Paragraph(
            "AI-Assisted Digital Image Forensics Report",
            styles["Heading2"],
        )
    )
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # 2. Overview
    # ---------------------------------------------------------
    story.append(Paragraph("1. Analysis Overview", heading_style))

    story.append(
        Paragraph(
            f"<b>File:</b> {safe_text(filename)}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Summary:</b> {safe_text(evidence.get('summary'))}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "<b>Review signals:</b> "
            + safe_text(evidence.get("review_signal_count", 0)),
            body_style,
        )
    )

    # ---------------------------------------------------------
    # 3. Unified risk score
    # ---------------------------------------------------------
    story.append(Paragraph("2. Explainable Risk Assessment", heading_style))

    if risk_score:
        score = risk_score.get("score", "Not available")
        level = risk_score.get("level", "Not available")
        interpretation = risk_score.get(
            "interpretation",
            "No interpretation available.",
        )

        score_table = Table(
            [
                ["Review-priority score", "Assessment level"],
                [f"{safe_text(score)} / 100", safe_text(level)],
            ],
            colWidths=[230, 230],
        )

        score_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#163A70"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("PADDING", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(score_table)
        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                safe_text(interpretation),
                body_style,
            )
        )

        reasons = risk_score.get("reasons", [])

        if isinstance(reasons, list) and reasons:
            story.append(Spacer(1, 6))
            story.append(Paragraph("<b>Reasons:</b>", body_style))

            for reason in reasons:
                story.append(
                    Paragraph(
                        f"&bull; {safe_text(reason)}",
                        body_style,
                    )
                )
                story.append(Spacer(1, 4))

        disclaimer = risk_score.get("disclaimer")

        if disclaimer:
            story.append(Spacer(1, 6))
            story.append(
                Paragraph(
                    f"<i>{safe_text(disclaimer)}</i>",
                    body_style,
                )
            )
    else:
        story.append(
            Paragraph(
                "The unified risk score was not supplied for this report.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # 4. Metadata
    # ---------------------------------------------------------
    story.append(Paragraph("3. Image Metadata", heading_style))

    metadata_rows = [
        ["Property", "Value"],
        ["Format", safe_text(metadata.get("format"))],
        ["Dimensions", safe_text(metadata.get("dimensions"))],
        ["Color mode", safe_text(metadata.get("mode"))],
        [
            "File size",
            safe_text(metadata.get("file_size_kb")) + " KB",
        ],
        ["EXIF available", safe_text(metadata.get("has_exif"))],
    ]

    metadata_table = Table(
        metadata_rows,
        colWidths=[150, 320],
    )

    metadata_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#163A70"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    story.append(metadata_table)

    # ---------------------------------------------------------
    # 5. Forensic findings
    # ---------------------------------------------------------
    story.append(Paragraph("4. Forensic Findings", heading_style))

    findings = evidence.get("findings", [])

    if isinstance(findings, list) and findings:
        for index, finding in enumerate(findings, start=1):
            if not isinstance(finding, dict):
                continue

            story.append(
                Paragraph(
                    f"<b>{index}. {safe_text(finding.get('method'))}</b>",
                    body_style,
                )
            )

            story.append(
                Paragraph(
                    f"<b>Status:</b> {safe_text(finding.get('status'))}",
                    body_style,
                )
            )

            story.append(
                Paragraph(
                    f"<b>Severity:</b> {safe_text(finding.get('severity'))}",
                    body_style,
                )
            )

            story.append(
                Paragraph(
                    safe_text(finding.get("observation")),
                    body_style,
                )
            )

            story.append(Spacer(1, 8))
    else:
        story.append(
            Paragraph(
                "No detailed forensic findings were supplied.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # 6. Typography analysis
    # ---------------------------------------------------------
    story.append(Paragraph("5. Screenshot Typography Analysis", heading_style))

    if typography.get("available") is True:
        story.append(
            Paragraph(
                f"<b>Status:</b> {safe_text(typography.get('status'))}",
                body_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Text-like components:</b> "
                f"{safe_text(typography.get('component_count'))}",
                body_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Detected text rows:</b> "
                f"{safe_text(typography.get('text_row_count'))}",
                body_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Observation:</b> "
                f"{safe_text(typography.get('observation'))}",
                body_style,
            )
        )

        typography_flags = typography.get("flags", [])

        if isinstance(typography_flags, list) and typography_flags:
            story.append(Spacer(1, 5))
            story.append(Paragraph("<b>Typography indicators:</b>", body_style))

            for flag in typography_flags:
                story.append(
                    Paragraph(
                        f"&bull; {safe_text(flag)}",
                        body_style,
                    )
                )
                story.append(Spacer(1, 4))

        add_visualization(
            story,
            "Typography Anomaly Overlay",
            typography,
            styles,
        )

        limitations = typography.get("limitations", [])

        if isinstance(limitations, list) and limitations:
            story.append(Paragraph("<b>Typography limitations:</b>", body_style))

            for limitation in limitations:
                story.append(
                    Paragraph(
                        f"&bull; {safe_text(limitation)}",
                        body_style,
                    )
                )
                story.append(Spacer(1, 4))
    else:
        story.append(
            Paragraph(
                "Typography analysis was not available for this report.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # 7. Analysis visualizations
    # ---------------------------------------------------------
    story.append(Paragraph("6. Analysis Visualizations", heading_style))

    visualization_items = [
        ("ELA Heatmap", ela),
        ("Local Noise Residual Map", noise),
        ("Edge Map", edges),
        ("Copy-Move Feature Matches", copy_move),
    ]

    for label, result in visualization_items:
        add_visualization(story, label, result, styles)

    # ---------------------------------------------------------
    # 8. Methodology and limitations
    # ---------------------------------------------------------
    story.append(PageBreak())

    story.append(Paragraph("7. Methodology", heading_style))

    methodology = [
        "Metadata analysis extracts image properties and available EXIF information.",
        "Error Level Analysis compares a JPEG image with a recompressed version.",
        "Noise residual analysis visualizes local high-frequency residual variation.",
        "Edge analysis highlights image boundaries using edge detection.",
        "Copy-move analysis searches for spatially separated similar image features.",
        "Typography analysis estimates text-like component consistency and layout characteristics.",
        "The unified score combines selected review indicators into an experimental review-priority score.",
    ]

    for item in methodology:
        story.append(
            Paragraph(
                f"&bull; {safe_text(item)}",
                body_style,
            )
        )
        story.append(Spacer(1, 5))

    story.append(Paragraph("8. Important Limitations", heading_style))

    evidence_limitations = evidence.get("limitations", [])

    if isinstance(evidence_limitations, list):
        for limitation in evidence_limitations:
            story.append(
                Paragraph(
                    f"&bull; {safe_text(limitation)}",
                    body_style,
                )
            )
            story.append(Spacer(1, 5))

    general_limitations = [
        "Automated indicators do not prove that an image has been manipulated.",
        "Typography measurements are approximate and do not identify an exact font.",
        "Screenshot resizing, compression, and display scaling can affect measurements.",
        "OCR errors and image quality can affect text-related analysis.",
        "The review-priority score is not a probability of forgery.",
        "A clean result does not guarantee that an image is authentic.",
    ]

    for limitation in general_limitations:
        story.append(
            Paragraph(
                f"&bull; {safe_text(limitation)}",
                body_style,
            )
        )
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Generated by VerifEye. This report is an automated "
            "image-analysis aid and should not be treated as a "
            "definitive authenticity certificate.",
            styles["Italic"],
        )
    )

    document.build(story)

    return str(destination)
