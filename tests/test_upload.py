
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app


client = TestClient(app)


def make_image(color="white", image_format="PNG"):
    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (100, 100),
        color=color
    )

    image.save(buffer, format=image_format)
    buffer.seek(0)

    return buffer


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_valid_png_upload():
    response = client.post(
        "/api/verify",
        files={
            "file": (
                "sample.png",
                make_image(),
                "image/png"
            )
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert "job_id" in result
    assert "metadata" in result
    assert "evidence" in result
    assert "artifacts" in result


def test_invalid_upload():
    response = client.post(
        "/api/verify",
        files={
            "file": (
                "fake.png",
                BytesIO(b"This is not an image"),
                "image/png"
            )
        }
    )

    assert response.status_code == 400


def test_compare_two_identical_images():
    response = client.post(
        "/api/compare",
        files={
            "first_file": (
                "first.png",
                make_image("white"),
                "image/png"
            ),
            "second_file": (
                "second.png",
                make_image("white"),
                "image/png"
            )
        }
    )

    assert response.status_code == 200

    result = response.json()
    comparison = result["comparison"]

    assert "job_id" in result
    assert comparison["ssim_score"] > 0.99
    assert comparison["changed_pixel_percentage"] == 0
    assert "difference_heatmap" in result["artifacts"]


def test_compare_different_images():
    response = client.post(
        "/api/compare",
        files={
            "first_file": (
                "first.png",
                make_image("white"),
                "image/png"
            ),
            "second_file": (
                "second.png",
                make_image("black"),
                "image/png"
            )
        }
    )

    assert response.status_code == 200

    comparison = response.json()["comparison"]

    assert comparison["ssim_score"] < 0.99
    assert comparison["changed_pixel_percentage"] > 0


def test_compare_rejects_invalid_image():
    response = client.post(
        "/api/compare",
        files={
            "first_file": (
                "first.png",
                make_image(),
                "image/png"
            ),
            "second_file": (
                "fake.png",
                BytesIO(b"Not an image"),
                "image/png"
            )
        }
    )

    assert response.status_code == 400
