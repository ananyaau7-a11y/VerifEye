from pathlib import Path

from backend.metadata import extract_metadata
from backend.ela import compute_ela
from backend.noise_analysis import analyze_noise
from backend.edge_analysis import analyze_edges
from backend.copy_move import detect_copy_move
from backend.evidence_engine import build_evidence
from backend.report_gen import generate_pdf_report


def run_full_analysis(image_path: str, output_dir: str) -> dict:
    """Run the complete VerifEye image analysis pipeline."""

    source = Path(image_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        raise FileNotFoundError("Input image does not exist.")

    # 1. Metadata
    metadata = extract_metadata(str(source))

    # 2. ELA
    ela_result = compute_ela(
        str(source),
        str(output / "ela_heatmap.png")
    )

    # 3. Local noise residual analysis
    noise_result = analyze_noise(
        str(source),
        str(output / "noise_map.png")
    )

    # 4. Edge analysis
    edge_result = analyze_edges(
        str(source),
        str(output / "edge_map.png")
    )

    # 5. Copy-move feature matching
    copy_move_result = detect_copy_move(
        str(source),
        str(output / "copy_move_matches.png")
    )

    # 6. Explainable evidence
    evidence = build_evidence(
        metadata,
        ela_result,
        noise_result,
        edge_result,
        copy_move_result
    )

    # 7. PDF report
    report_path = generate_pdf_report(
        filename=source.name,
        metadata=metadata,
        ela=ela_result,
        noise=noise_result,
        edges=edge_result,
        copy_move=copy_move_result,
        evidence=evidence,
        output_path=str(output / "forensic_report.pdf")
    )

    return {
        "filename": source.name,
        "metadata": metadata,
        "ela_analysis": ela_result,
        "noise_analysis": noise_result,
        "edge_analysis": edge_result,
        "copy_move_analysis": copy_move_result,
        "evidence": evidence,
        "artifacts": {
            "ela_heatmap": (
                "ela_heatmap.png"
                if ela_result.get("available")
                else None
            ),
            "noise_map": "noise_map.png",
            "edge_map": "edge_map.png",
            "copy_move_matches": "copy_move_matches.png",
            "pdf_report": Path(report_path).name
        }
    }