from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance
import numpy as np


def compute_ela(
    image_path: str,
    output_path: str,
    quality: int = 90
) -> dict:
    """
    Generate an Error Level Analysis heatmap.

    ELA is intended for JPEG source images.
    """

    source = Path(image_path)
    destination = Path(output_path)

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(source) as image:
            image_format = image.format

            if image_format != "JPEG":
                return {
                    "available": False,
                    "reason": (
                        "Standard JPEG ELA is not directly applicable "
                        f"to {image_format or 'this'} image."
                    ),
                    "output_path": None
                }

            original = image.convert("RGB")

        # Recompress in memory instead of creating a shared temporary file.
        import io

        buffer = io.BytesIO()
        original.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)

        with Image.open(buffer) as compressed_image:
            compressed = compressed_image.convert("RGB")

        difference = ImageChops.difference(original, compressed)

        extrema = difference.getextrema()
        maximum_difference = max(channel[1] for channel in extrema)

        if maximum_difference == 0:
            maximum_difference = 1

        scale = 255.0 / maximum_difference

        ela_image = ImageEnhance.Brightness(difference).enhance(scale)

        ela_image.save(destination, format="PNG")

        diff_array = np.asarray(difference, dtype=np.float32)

        return {
            "available": True,
            "output_path": str(destination),
            "quality": quality,
            "mean_difference": round(float(diff_array.mean()), 4),
            "maximum_difference": int(maximum_difference),
            "explanation": (
                "The heatmap visualizes differences after JPEG "
                "recompression. Bright regions may deserve inspection, "
                "but are not proof of manipulation."
            )
        }

    except Exception as error:
        raise ValueError(f"ELA generation failed: {error}") from error