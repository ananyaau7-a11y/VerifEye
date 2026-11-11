from pathlib import Path
from PIL import Image

from backend.metadata import extract_metadata
from backend.ela import compute_ela
from backend.noise_analysis import analyze_noise
from backend.edge_analysis import analyze_edges


def create_test_image(path, image_format="PNG"):
    image = Image.new("RGB", (200, 200), color="white")
    image.save(path, format=image_format)


def test_metadata_extraction(tmp_path):
    image_path = tmp_path / "test.png"
    create_test_image(image_path)

    result = extract_metadata(str(image_path))

    assert result["format"] == "PNG"
    assert result["width"] == 200
    assert result["height"] == 200


def test_png_ela_not_applicable(tmp_path):
    image_path = tmp_path / "test.png"
    output_path = tmp_path / "ela.png"

    create_test_image(image_path)

    result = compute_ela(
        str(image_path),
        str(output_path)
    )

    assert result["available"] is False


def test_jpeg_ela_generation(tmp_path):
    image_path = tmp_path / "test.jpg"
    output_path = tmp_path / "ela.png"

    create_test_image(image_path, "JPEG")

    result = compute_ela(
        str(image_path),
        str(output_path)
    )

    assert result["available"] is True
    assert Path(result["output_path"]).exists()


def test_noise_map_generation(tmp_path):
    image_path = tmp_path / "test.png"
    output_path = tmp_path / "noise.png"

    create_test_image(image_path)

    result = analyze_noise(
        str(image_path),
        str(output_path)
    )

    assert Path(result["output_path"]).exists()
    assert "mean_residual" in result


def test_edge_map_generation(tmp_path):
    image_path = tmp_path / "test.png"
    output_path = tmp_path / "edges.png"

    create_test_image(image_path)

    result = analyze_edges(
        str(image_path),
        str(output_path)
    )

    assert Path(result["output_path"]).exists()
    assert "edge_density" in result