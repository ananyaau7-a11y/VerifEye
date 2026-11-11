from pathlib import Path
import cv2
import numpy as np


def analyze_noise(image_path: str, output_path: str) -> dict:
    """
    Analyze local high-frequency residual patterns.

    This is an exploratory forensic indicator, not a
    standalone image manipulation detector.
    """

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Unable to read image for noise analysis.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Estimate smooth image content.
    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        sigmaX=1.0
    )

    # High-frequency residual.
    residual = cv2.absdiff(gray, blurred)

    # Calculate local residual variation.
    residual_float = residual.astype(np.float32)

    local_mean = cv2.blur(residual_float, (15, 15))
    local_squared_mean = cv2.blur(
        residual_float ** 2,
        (15, 15)
    )

    local_variance = np.maximum(
        local_squared_mean - local_mean ** 2,
        0
    )

    local_std = np.sqrt(local_variance)

    # Normalize for visualization only.
    normalized = cv2.normalize(
        local_std,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    heatmap = cv2.applyColorMap(
        normalized.astype(np.uint8),
        cv2.COLORMAP_TURBO
    )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(destination), heatmap):
        raise ValueError("Unable to save noise residual map.")

    return {
        "output_path": str(destination),
        "mean_residual": round(float(residual_float.mean()), 3),
        "mean_local_variation": round(float(local_std.mean()), 3),
        "maximum_local_variation": round(float(local_std.max()), 3),
        "explanation": (
            "The map visualizes local high-frequency residual variation. "
            "Differences may result from texture, compression, lighting, "
            "or editing. They require contextual inspection."
        )
    }