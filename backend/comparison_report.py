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
    HRFlowable,
    KeepTogether,
)


def _safe_paragraph(value, style):
    """Create a ReportLab paragraph without interpreting user/OCR text as markup."""
    return Paragraph(escape(str(value if value is not None else "N/A")), style)


def _add_bullet_list(story, items, styles):
    for item in items:
        story.append(
            Paragraph(
                "- " + escape(str(item)),
                styles["Normal"]
            )
        )
        story.append(Spacer(1, 5))


def _format_ocr_text(image_result):
    if not isinstance(image_result, dict):
        return "OCR details are unavailable."

    text = str(image_result.get("text", "")).strip()
    if not text:
        return "No readable text was detected in this image."

    # Keep the report readable if a screenshot contains a large amount of text.
    max_chars = 5000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n[Text truncated in this report.]"

    return text


def generate_comparison_report(
    first_image: dict,
    second_image: dict,
    comparison: dict,
    output_path: str
) -> str:

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#163A63"),
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#163A63"),
            spaceBefore=15,
            spaceAfter=8
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["Normal"],
            fontSize=8,
            leading=11
        )
    )

    styles.add(
        ParagraphStyle(
            name="OCRText",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            leftIndent=6,
            rightIndent=6,
            wordWrap="CJK"
        )
    )

    story = []

    # 1. TITLE
    story.append(
        Paragraph(
            "VerifEye Comparison Forensic Report",
            styles["ReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "AI-Assisted Digital Image Forensics",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 12))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#2563EB")
        )
    )

    # 2. REPORT OVERVIEW
    story.append(
        Paragraph("1. Report Overview", styles["SectionHeading"])
    )

    story.append(
        Paragraph(
            "This report documents the results of a comparison between "
            "two uploaded images using structural similarity, "
            "pixel-difference analysis and OCR-based text comparison.",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 10))

    # 3. IMAGE INFORMATION
    story.append(
        Paragraph(
            "2. Uploaded Image Information",
            styles["SectionHeading"]
        )
    )

    image_data = [
        ["Property", "First Image", "Second Image"],
        [
            "Filename",
            escape(str(first_image.get("filename", "Unknown"))),
            escape(str(second_image.get("filename", "Unknown")))
        ],
        [
            "Format",
            escape(str(first_image.get("format", "Unknown"))),
            escape(str(second_image.get("format", "Unknown")))
        ],
        [
            "Dimensions",
            escape(str(first_image.get("dimensions", "Unknown"))),
            escape(str(second_image.get("dimensions", "Unknown")))
        ],
        [
            "File Size",
            escape(str(first_image.get("file_size_kb", "Unknown"))) + " KB",
            escape(str(second_image.get("file_size_kb", "Unknown"))) + " KB"
        ]
    ]

    image_table = Table(
        image_data,
        colWidths=[1.3 * inch, 2.2 * inch, 2.2 * inch]
    )

    image_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A63")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("PADDING", (0, 0), (-1, -1), 7)
        ])
    )

    story.append(image_table)
    story.append(Spacer(1, 12))

    # 4. VISUAL COMPARISON METRICS
    story.append(
        Paragraph(
            "3. Visual Comparison Results",
            styles["SectionHeading"]
        )
    )

    metrics_data = [
        ["Metric", "Result"],
        [
            "Structural Similarity",
            escape(str(comparison.get("similarity_percentage", 0))) + "%"
        ],
        [
            "SSIM Score",
            escape(str(comparison.get("ssim_score", "N/A")))
        ],
        [
            "Changed Pixel Percentage",
            escape(str(comparison.get("changed_pixel_percentage", 0))) + "%"
        ],
        [
            "Changed Pixel Count",
            escape(str(comparison.get("changed_pixel_count", "N/A")))
        ],
        [
            "Changed Regions",
            escape(str(comparison.get("changed_region_count", 0)))
        ],
        [
            "Original Dimensions Match",
            escape(str(comparison.get("same_dimensions_originally", "N/A")))
        ]
    ]

    metrics_table = Table(
        metrics_data,
        colWidths=[3 * inch, 2.5 * inch]
    )

    metrics_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A63")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 7)
        ])
    )

    story.append(metrics_table)
    story.append(Spacer(1, 12))

    # 5. DIFFERENCE HEATMAP
    story.append(
        Paragraph("4. Difference Heatmap", styles["SectionHeading"])
    )

    heatmap_name = comparison.get("difference_heatmap", "")
    heatmap_path = output_path.parent / heatmap_name if heatmap_name else None

    if heatmap_path and heatmap_path.exists():
        heatmap = ReportImage(
            str(heatmap_path),
            width=5.5 * inch,
            height=3.5 * inch,
            kind="proportional"
        )
        story.append(heatmap)
        story.append(Spacer(1, 8))
        story.append(
            Paragraph(
                "The heatmap highlights areas with pixel-level "
                "differences between the uploaded images.",
                styles["SmallText"]
            )
        )
    else:
        story.append(
            Paragraph(
                "Difference heatmap was not available.",
                styles["Normal"]
            )
        )

    # 6. CHANGED REGIONS
    story.append(
        Paragraph(
            "5. Changed Region Details",
            styles["SectionHeading"]
        )
    )

    regions = comparison.get("changed_regions", [])

    if regions:
        region_data = [
            ["Region", "X", "Y", "Width", "Height", "Area"]
        ]

        for index, region in enumerate(regions, start=1):
            region_data.append([
                str(index),
                str(region.get("x", "N/A")),
                str(region.get("y", "N/A")),
                str(region.get("width", "N/A")),
                str(region.get("height", "N/A")),
                str(region.get("area", "N/A"))
            ])

        region_table = Table(
            region_data,
            repeatRows=1,
            colWidths=[
                0.65 * inch,
                0.7 * inch,
                0.7 * inch,
                0.8 * inch,
                0.8 * inch,
                0.9 * inch
            ]
        )

        region_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
            ])
        )

        story.append(region_table)
    else:
        story.append(
            Paragraph(
                "No significant changed regions were detected using "
                "the configured threshold.",
                styles["Normal"]
            )
        )

    # 7. OCR TEXT COMPARISON
    story.append(
        Paragraph(
            "6. OCR Text Comparison",
            styles["SectionHeading"]
        )
    )

    ocr = comparison.get("ocr_comparison", {})

    if isinstance(ocr, dict) and ocr.get("available"):
        story.append(
            Paragraph(
                escape(str(ocr.get(
                    "assessment",
                    "OCR comparison completed. Review the extracted text below."
                ))),
                styles["Normal"]
            )
        )
        story.append(Spacer(1, 8))

        first_ocr = ocr.get("first_image", {})
        second_ocr = ocr.get("second_image", {})

        ocr_metrics = [
            ["OCR Detail", "First Image", "Second Image"],
            [
                "Words Detected",
                str(first_ocr.get("words_detected", 0)),
                str(second_ocr.get("words_detected", 0))
            ],
            [
                "Average Confidence",
                str(first_ocr.get("average_confidence", 0)) + "%",
                str(second_ocr.get("average_confidence", 0)) + "%"
            ],
            [
                "Extraction Status",
                escape(str(first_ocr.get("extraction_status", "Unknown"))),
                escape(str(second_ocr.get("extraction_status", "Unknown")))
            ]
        ]

        ocr_metrics_table = Table(
            ocr_metrics,
            colWidths=[1.5 * inch, 2.0 * inch, 2.0 * inch]
        )
        ocr_metrics_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP")
            ])
        )
        story.append(ocr_metrics_table)
        story.append(Spacer(1, 10))

        story.append(
            Paragraph("Extracted Text - First Image", styles["Heading3"])
        )
        story.append(
            _safe_paragraph(_format_ocr_text(first_ocr), styles["OCRText"])
        )
        story.append(Spacer(1, 8))

        story.append(
            Paragraph("Extracted Text - Second Image", styles["Heading3"])
        )
        story.append(
            _safe_paragraph(_format_ocr_text(second_ocr), styles["OCRText"])
        )
        story.append(Spacer(1, 10))

        added = ocr.get("added_text", [])
        removed = ocr.get("removed_text", [])
        modified = ocr.get("modified_text", [])

        story.append(Paragraph("Detected Text Changes", styles["Heading3"]))

        change_summary = [
            ["Change Type", "Count"],
            ["Added words", str(ocr.get("added_word_count", len(added)))],
            ["Removed words", str(ocr.get("removed_word_count", len(removed)))],
            [
                "Modified segments",
                str(ocr.get("modified_segment_count", len(modified)))
            ]
        ]

        change_table = Table(change_summary, colWidths=[3 * inch, 2.5 * inch])
        change_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("PADDING", (0, 0), (-1, -1), 6)
            ])
        )
        story.append(change_table)
        story.append(Spacer(1, 8))

        if added:
            story.append(Paragraph("Added Text", styles["Heading4"]))
            _add_bullet_list(story, added[:40], styles)

        if removed:
            story.append(Paragraph("Removed Text", styles["Heading4"]))
            _add_bullet_list(story, removed[:40], styles)

        if modified:
            story.append(Paragraph("Modified Text Segments", styles["Heading4"]))
            for item in modified[:30]:
                old_text = escape(str(item.get("first_image_text", "")))
                new_text = escape(str(item.get("second_image_text", "")))
                story.append(
                    Paragraph(
                        "<b>First image:</b> " + old_text +
                        "<br/><b>Second image:</b> " + new_text,
                        styles["SmallText"]
                    )
                )
                story.append(Spacer(1, 5))

        ocr_limitations = ocr.get("limitations", [])
        if ocr_limitations:
            story.append(
                Paragraph("OCR Limitations", styles["Heading3"])
            )
            _add_bullet_list(story, ocr_limitations, styles)

    else:
        unavailable_reason = (
            ocr.get("error", "OCR comparison was not included in this report.")
            if isinstance(ocr, dict)
            else "OCR comparison was not included in this report."
        )
        story.append(
            Paragraph(
                "OCR comparison was unavailable for this report. " +
                escape(str(unavailable_reason)),
                styles["Normal"]
            )
        )

    # 8. METHODOLOGY
    story.append(
        Paragraph("7. Methodology", styles["SectionHeading"])
    )

    methodology = [
        "Structural Similarity Index (SSIM) compares structural "
        "information between the images.",
        "Pixel-difference analysis measures the absolute difference "
        "between corresponding pixel values.",
        "Changed-region analysis groups detected pixel differences "
        "into connected candidate regions.",
        "OCR extracts machine-readable text from both images and "
        "compares the resulting word sequences for possible additions, "
        "removals or modifications."
    ]

    _add_bullet_list(story, methodology, styles)

    # 9. LIMITATIONS
    story.append(
        Paragraph("8. Important Limitations", styles["SectionHeading"])
    )

    limitations = [
        "A difference between two images does not establish which "
        "image is original or authentic.",
        "SSIM and pixel-difference measurements are not independent "
        "proof of image manipulation.",
        "Images with different dimensions are resized for comparison, "
        "which may influence results.",
        "Compression, resizing, brightness changes and normal editing "
        "can also produce differences.",
        "OCR may misread digits, symbols, small text or low-quality "
        "content. Text order and layout can also affect comparison.",
        "A detected OCR text difference does not prove manipulation, "
        "and OCR cannot establish which image is authentic.",
        "The report should be interpreted alongside trusted source "
        "files and additional evidence."
    ]

    _add_bullet_list(story, limitations, styles)

    # 10. DISCLAIMER
    story.append(Spacer(1, 15))
    story.append(
        HRFlowable(
            width="100%",
            thickness=0.7,
            color=colors.grey
        )
    )
    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "<b>Disclaimer:</b> VerifEye is an experimental "
            "AI-assisted image-forensics tool. This report provides "
            "technical observations and indicators for further "
            "investigation. It is not a certified forensic conclusion "
            "and does not guarantee image authenticity. OCR and visual "
            "comparison results require human review.",
            styles["SmallText"]
        )
    )

    document.build(story)

    return str(output_path)
