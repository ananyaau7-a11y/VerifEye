
from pathlib import Path

from PIL import Image, ImageDraw

from backend.similarity import compare_images


def create_test_image(path, modified=False):
    image = Image.new(
        "RGB",
        (200, 200),
        color="white"
    )

    if modified:
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (50, 50, 120, 120),
            fill="black"
        )

    image.save(path)


def test_identical_image_comparison(tmp_path):
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"

    create_test_image(first)
    create_test_image(second)

    result = compare_images(
        str(first),
        str(second),
        str(tmp_path / "output")
    )

    assert result["ssim_score"] > 0.99
    assert result["changed_pixel_percentage"] == 0
    assert Path(
        tmp_path / "output" / "difference_heatmap.png"
    ).exists()


def test_modified_image_comparison(tmp_path):
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"

    create_test_image(first)
    create_test_image(second, modified=True)

    result = compare_images(
        str(first),
        str(second),
        str(tmp_path / "output")
    )

    assert result["ssim_score"] < 1.0
    assert result["changed_pixel_percentage"] > 0
    assert result["changed_region_count"] > 0
