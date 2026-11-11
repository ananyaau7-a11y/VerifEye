
from pathlib import Path
import cv2
import numpy as np


def analyze_edges(image_path: str, output_path: str) -> dict:
    """Generate an edge map using Canny edge detection."""

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Unable to read image for edge analysis.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(
        blurred,
        threshold1=80,
        threshold2=160
    )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(destination), edges):
        raise ValueError("Unable to save edge map.")

    edge_pixels = int(np.count_nonzero(edges))
    total_pixels = int(edges.size)

    edge_density = (
        edge_pixels / total_pixels
        if total_pixels else 0
    )

    return {
        "output_path": str(destination),
        "edge_pixels": edge_pixels,
        "edge_density": round(edge_density, 5),
        "explanation": (
            "The edge map highlights image boundaries and transitions. "
            "Unusual boundaries may warrant inspection, but natural "
            "objects and text also produce strong edges."
        )
    }
