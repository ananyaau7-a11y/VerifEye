from PIL import Image, ExifTags
from datetime import datetime
from pathlib import Path
from typing import Any


def make_json_safe(value: Any):
    """Convert EXIF values into JSON-serializable values."""

    if isinstance(value, bytes):
        return value.hex()

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, (tuple, list)):
        return [make_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(val)
            for key, val in value.items()
        }

    return str(value)


def extract_metadata(image_path: str) -> dict:
    """Extract image properties and available EXIF metadata."""

    path = Path(image_path)

    try:
        with Image.open(path) as image:
            exif_data = image.getexif()

            exif = {}

            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                exif[tag_name] = make_json_safe(value)

            metadata = {
                "filename": path.name,
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "dimensions": f"{image.width} x {image.height}",
                "file_size_bytes": path.stat().st_size,
                "file_size_kb": round(path.stat().st_size / 1024, 2),
                "has_exif": bool(exif),
                "exif": exif,
                "warnings": []
            }

            if not exif:
                metadata["warnings"].append(
                    "No EXIF metadata was found. "
                    "This is common for screenshots and social-media images "
                    "and does not independently indicate manipulation."
                )

            if image.format not in ("JPEG", "PNG", "WEBP"):
                metadata["warnings"].append(
                    "This image format has limited support in this analysis."
                )

            return metadata

    except Exception as error:
        raise ValueError(
            f"Unable to extract image metadata: {error}"
        ) from error