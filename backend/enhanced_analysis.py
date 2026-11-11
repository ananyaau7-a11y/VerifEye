
from pathlib import Path

from backend.analysis import run_full_analysis
from backend.typography_analysis import analyze_typography
from backend.risk_scoring import calculate_risk_score
from backend.report_gen import generate_pdf_report


def run_enhanced_analysis(image_path: str, output_dir: str) -> dict:
    """
    Run the original VerifEye pipeline and extend it with
    typography analysis, risk scoring, and an upgraded PDF.
    """

    output_directory = Path(output_dir)
    output_directory.mkdir(parents=True, exist_ok=True)

    # 1. Run the existing analysis without changing its logic.
    result = run_full_analysis(
        str(image_path),
        str(output_directory),
    )

    if not isinstance(result, dict):
        raise ValueError("The existing analysis returned an invalid result.")

    # 2. Run typography analysis.
    typography_path = output_directory / "typography_overlay.png"

    typography = analyze_typography(
        str(image_path),
        str(typography_path),
    )

    # 3. Calculate the experimental review-priority score.
    evidence = result.get("evidence", {})

    risk_score = calculate_risk_score(
        evidence,
        typography,
    )

    # 4. Retrieve existing analysis results.
    metadata = result.get("metadata", {})
    ela = result.get("ela_analysis", {})
    noise = result.get("noise_analysis", {})
    edges = result.get("edge_analysis", {})
    copy_move = result.get("copy_move_analysis", {})

    # 5. Preserve existing artifact filenames.
    artifacts = result.get("artifacts", {})

    if not isinstance(artifacts, dict):
        artifacts = {}

    # 6. Find the existing PDF filename.
    existing_pdf = artifacts.get("pdf_report")

    if existing_pdf:
        existing_path = Path(str(existing_pdf))

        if existing_path.is_absolute():
            pdf_path = existing_path
        else:
            pdf_path = output_directory / existing_path.name
    else:
        filename = result.get("filename", Path(image_path).name)
        pdf_path = output_directory / (
            f"{Path(filename).stem}_report.pdf"
        )

    # 7. Generate the upgraded PDF.
    generated_pdf = generate_pdf_report(
        filename=result.get("filename", Path(image_path).name),
        metadata=metadata,
        ela=ela,
        noise=noise,
        edges=edges,
        copy_move=copy_move,
        evidence=evidence,
        output_path=str(pdf_path),
        typography=typography,
        risk_score=risk_score,
    )

    # 8. Add new analysis results.
    result["typography_analysis"] = typography
    result["risk_score"] = risk_score

    # Store filenames, not absolute paths.
    artifacts["typography_overlay"] = Path(
        typography.get("output_path", typography_path)
    ).name

    artifacts["pdf_report"] = Path(generated_pdf).name

    result["artifacts"] = artifacts

    return result
