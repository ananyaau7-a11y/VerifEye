
def calculate_risk_score(evidence: dict, typography: dict | None = None) -> dict:
    """
    Calculate an explainable experimental image-review score.

    This is NOT a probability of manipulation or a verdict.
    Only explicit review signals contribute to the score.
    """

    score = 0
    reasons = []

    evidence = evidence if isinstance(evidence, dict) else {}
    typography = typography if isinstance(typography, dict) else {}

    # 1. Existing evidence-engine review findings.
    findings = evidence.get("findings", [])

    if isinstance(findings, list):
        for finding in findings:
            if not isinstance(finding, dict):
                continue

            severity = str(finding.get("severity", "")).strip().lower()

            if severity == "review":
                method = str(finding.get("method", "Forensic analysis"))
                score += 20
                reasons.append(
                    f"{method}: a review-level indicator was reported."
                )

            elif severity in ("high", "critical"):
                method = str(finding.get("method", "Forensic analysis"))
                score += 30
                reasons.append(
                    f"{method}: a high-severity indicator was reported."
                )

    # 2. Typography analysis.
    if typography.get("available") is True:
        try:
            typography_points = int(typography.get("risk_points", 0))
        except (TypeError, ValueError):
            typography_points = 0

        typography_points = max(0, min(35, typography_points))

        if typography.get("anomaly_detected") is True and typography_points > 0:
            score += typography_points

            flags = typography.get("flags", [])
            if isinstance(flags, list) and flags:
                for flag in flags[:4]:
                    reasons.append(f"Typography: {flag}")
            else:
                reasons.append(
                    "Typography analysis detected unusual text-layout characteristics."
                )

    # 3. Keep the score within 0–100.
    score = max(0, min(100, score))

    # 4. Human-readable interpretation.
    if score >= 70:
        level = "High review priority"
        interpretation = (
            "Several review indicators were detected. "
            "Inspect the highlighted regions and original source."
        )
    elif score >= 40:
        level = "Moderate review priority"
        interpretation = (
            "Some indicators warrant closer manual inspection."
        )
    elif score > 0:
        level = "Low review priority"
        interpretation = (
            "A limited number of indicators were detected. "
            "Review them in context."
        )
    else:
        level = "No review indicators detected"
        interpretation = (
            "The implemented checks did not report a review-level signal. "
            "This does not establish that the image is genuine."
        )

    if not reasons:
        reasons.append(
            "No explicit review-level indicators were reported by the available checks."
        )

    return {
        "score": score,
        "level": level,
        "interpretation": interpretation,
        "reasons": reasons,
        "is_probability": False,
        "disclaimer": (
            "Experimental review-priority score, not a probability of "
            "manipulation or a definitive authenticity verdict."
        )
    }
