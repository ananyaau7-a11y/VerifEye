
def build_evidence(
    metadata: dict,
    ela: dict,
    noise: dict,
    edges: dict,
    copy_move: dict
) -> dict:
    """Convert forensic analysis outputs into explainable findings."""

    findings = []

    # Metadata analysis
    if metadata.get("has_exif", False):
        findings.append({
            "method": "Metadata analysis",
            "status": "Metadata available",
            "severity": "Informational",
            "observation": (
                "EXIF metadata is available for inspection. "
                "Metadata presence does not establish authenticity."
            )
        })
    else:
        findings.append({
            "method": "Metadata analysis",
            "status": "Information unavailable",
            "severity": "Inconclusive",
            "observation": (
                "No EXIF metadata was found. This is common for "
                "screenshots and images shared through messaging applications."
            )
        })

    # ELA analysis
    if ela.get("available", False):
        findings.append({
            "method": "Error Level Analysis",
            "status": "Analysis completed",
            "severity": "Informational",
            "observation": (
                "An ELA heatmap was generated successfully. "
                "Visual inspection is required to determine whether "
                "any unusual compression patterns are present."
            )
        })
    else:
        findings.append({
            "method": "Error Level Analysis",
            "status": "Not applicable",
            "severity": "Inconclusive",
            "observation": ela.get(
                "reason",
                "ELA could not be performed."
            )
        })

    # Noise analysis
    if noise and noise.get("output_path"):
        findings.append({
            "method": "Local noise residual analysis",
            "status": "Analysis completed",
            "severity": "Informational",
            "observation": (
                "A local noise residual map was generated successfully. "
                "Differences in noise patterns require contextual inspection."
            )
        })
    else:
        findings.append({
            "method": "Local noise residual analysis",
            "status": "Unavailable",
            "severity": "Inconclusive",
            "observation": (
                "Noise residual analysis could not be completed."
            )
        })

    # Edge analysis
    if edges and edges.get("output_path"):
        findings.append({
            "method": "Edge analysis",
            "status": "Analysis completed",
            "severity": "Informational",
            "observation": (
                "An edge map was generated successfully. "
                "Object boundaries and transitions can be inspected visually."
            )
        })
    else:
        findings.append({
            "method": "Edge analysis",
            "status": "Unavailable",
            "severity": "Inconclusive",
            "observation": (
                "Edge analysis could not be completed."
            )
        })

    # Copy-move analysis
    if copy_move.get("available", False):
        candidate = copy_move.get("candidate_detected", False)

        findings.append({
            "method": "Copy-move feature matching",
            "status": (
                "Potential candidate matches found"
                if candidate
                else "No strong candidate matches"
            ),
            "severity": (
                "Review"
                if candidate
                else "Informational"
            ),
            "observation": (
                f"{copy_move.get('possible_duplicate_matches', 0)} "
                "spatially separated feature matches were identified. "
                "Repeated natural patterns can produce similar matches, "
                "so manual verification is necessary."
            )
        })
    else:
        findings.append({
            "method": "Copy-move feature matching",
            "status": "Unavailable",
            "severity": "Inconclusive",
            "observation": copy_move.get(
                "explanation",
                "Feature matching could not be completed."
            )
        })

    # Count only potential anomaly indicators
    review_count = sum(
        1 for finding in findings
        if finding["severity"] == "Review"
    )

    inconclusive_count = sum(
        1 for finding in findings
        if finding["severity"] == "Inconclusive"
    )

    if review_count >= 2:
        summary = "Multiple potential indicators warrant manual review"
    elif review_count == 1:
        summary = "A potential indicator warrants manual review"
    elif inconclusive_count > 0:
        summary = "Analysis is incomplete or inconclusive"
    else:
        summary = "No potential indicators were detected by the implemented checks"

    return {
        "summary": summary,
        "review_signal_count": review_count,
        "inconclusive_count": inconclusive_count,
        "findings": findings,
        "limitations": [
            "Automated image analysis cannot guarantee authenticity.",
            "Compression, resizing, screenshots and editing can affect results.",
            "Natural image content can trigger false positives.",
            "A lack of detected anomalies does not prove an image is authentic.",
            "Generated visualizations are inspection aids, not proof of manipulation.",
            "Findings should be reviewed alongside the original source and context."
        ]
    }
