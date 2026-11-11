
from pathlib import Path

import cv2
import numpy as np


def analyze_typography(image_path: str, output_path: str) -> dict:
    """
    Experimental screenshot typography consistency analysis.

    Checks:
    1. Text component height variation
    2. Approximate text-line baseline alignment
    3. Unusual spacing between detected components
    4. Edge-rendering consistency

    These are heuristic indicators, not proof of manipulation.
    """

    source = Path(image_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(str(source))

    if image is None:
        return {
            "available": False,
            "reason": "Unable to read the supplied image.",
            "anomaly_detected": False,
            "risk_points": 0,
        }

    original_height, original_width = image.shape[:2]

    # Limit processing size for performance.
    scale = min(1.0, 1600 / max(original_height, original_width))

    if scale < 1.0:
        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA,
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        11,
    )

    count, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(binary, 8)
    )

    height, width = gray.shape

    components = []

    for index in range(1, count):
        x, y, w, h, area = stats[index]

        if area < 5:
            continue

        if h < 5 or h > height * 0.12:
            continue

        if w > width * 0.15:
            continue

        if area > height * width * 0.01:
            continue

        components.append({
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
            "area": int(area),
            "center_y": float(y + h / 2),
            "bottom": float(y + h),
        })

    overlay = image.copy()

    if len(components) < 12:
        cv2.imwrite(str(destination), overlay)

        return {
            "available": False,
            "reason": (
                "Insufficient text-like components were detected. "
                "This check is more suitable for screenshots containing text."
            ),
            "anomaly_detected": False,
            "risk_points": 0,
            "component_count": len(components),
            "output_path": str(destination),
        }

    heights = np.array(
        [item["h"] for item in components],
        dtype=np.float32,
    )

    median_height = float(np.median(heights))

    # 1. Text component size variation.
    q1, q3 = np.percentile(heights, [25, 75])

    height_spread = float(
        (q3 - q1) / max(median_height, 1)
    )

    unusual_components = []

    for item in components:
        if abs(item["h"] - median_height) > max(
            3, median_height * 0.55
        ):
            unusual_components.append(item)

            cv2.rectangle(
                overlay,
                (item["x"], item["y"]),
                (
                    item["x"] + item["w"],
                    item["y"] + item["h"],
                ),
                (30, 70, 240),
                1,
            )

    unusual_ratio = (
        len(unusual_components) / len(components)
    )

    # 2. Approximate text-row and baseline consistency.
    sorted_components = sorted(
        components,
        key=lambda item: item["center_y"],
    )

    rows = []

    for item in sorted_components:
        matched_row = None

        for row in rows:
            if abs(
                item["center_y"] - row["center"]
            ) <= max(4, median_height * 0.45):
                matched_row = row
                break

        if matched_row is None:
            rows.append({
                "center": item["center_y"],
                "items": [item],
            })
        else:
            matched_row["items"].append(item)

            matched_row["center"] = float(
                np.mean([
                    component["center_y"]
                    for component in matched_row["items"]
                ])
            )

    baseline_deviations = []

    for row in rows:
        if len(row["items"]) < 3:
            continue

        bottoms = np.array(
            [item["bottom"] for item in row["items"]],
            dtype=np.float32,
        )

        median_bottom = float(np.median(bottoms))

        baseline_deviations.extend(
            np.abs(bottoms - median_bottom).tolist()
        )

    baseline_spread = (
        float(
            np.percentile(baseline_deviations, 90)
            / max(median_height, 1)
        )
        if baseline_deviations
        else 0.0
    )

    # 3. Approximate horizontal spacing variation.
    spacing_values = []

    for row in rows:
        row_items = sorted(
            row["items"],
            key=lambda item: item["x"],
        )

        for first, second in zip(
            row_items,
            row_items[1:],
        ):
            gap = second["x"] - (
                first["x"] + first["w"]
            )

            # Ignore overlapping or extremely distant components.
            if 0 <= gap <= median_height * 2:
                spacing_values.append(gap)

    spacing_spread = 0.0

    if len(spacing_values) >= 5:
        spacing_array = np.array(
            spacing_values,
            dtype=np.float32,
        )

        spacing_spread = float(
            np.std(spacing_array)
            / max(np.mean(spacing_array), 1)
        )

    # 4. Approximate edge transition measurement.
    edges = cv2.Canny(gray, 60, 150)

    edge_area = cv2.dilate(
        edges,
        np.ones((3, 3), np.uint8),
        iterations=1,
    ) > 0

    edge_pixels = gray[edge_area]

    antialias_ratio = 0.0

    if edge_pixels.size:
        antialias_ratio = float(
            np.mean(
                (edge_pixels > 15)
                & (edge_pixels < 240)
            )
        )

    # Heuristic flags. Thresholds are preliminary and require evaluation.
    flags = []

    if height_spread > 0.90:
        flags.append(
            "Unusual variation in text-component heights"
        )

    if baseline_spread > 0.35:
        flags.append(
            "Possible text-row baseline inconsistency"
        )

    if unusual_ratio > 0.28:
        flags.append(
            "Many text components differ from the median height"
        )

    if spacing_spread > 1.5:
        flags.append(
            "High variation in approximate component spacing"
        )

    # Transparent experimental points, not a probability.
    risk_points = 0

    if height_spread > 0.90:
        risk_points += 8

    if baseline_spread > 0.35:
        risk_points += 8

    if unusual_ratio > 0.28:
        risk_points += 8

    if spacing_spread > 1.5:
        risk_points += 6

    risk_points = min(risk_points, 30)

    cv2.imwrite(str(destination), overlay)

    return {
        "available": True,
        "status": "completed",
        "anomaly_detected": bool(flags),
        "risk_points": risk_points,
        "component_count": len(components),
        "text_row_count": len(rows),
        "median_component_height": round(
            median_height, 2
        ),
        "height_spread": round(height_spread, 3),
        "baseline_spread": round(baseline_spread, 3),
        "unusual_component_ratio": round(
            unusual_ratio, 3
        ),
        "spacing_spread": round(spacing_spread, 3),
        "antialiasing_edge_ratio": round(
            antialias_ratio, 3
        ),
        "flags": flags,
        "observation": (
            "; ".join(flags)
            if flags
            else "No strong typography inconsistency was detected."
        ),
        "explanation": (
            "Red boxes identify text-like components with unusual "
            "height. Measurements are approximate and can be affected "
            "by legitimate UI styling, font sizes, scaling and compression."
        ),
        "output_path": str(destination),
        "limitations": [
            "This prototype does not identify exact font families.",
            "Kerning cannot be reliably identified from arbitrary screenshots using these measurements alone.",
            "Different headings, labels and buttons naturally have different sizes.",
            "Operating-system rendering, image scaling and compression affect edge measurements.",
            "A flagged component is an inspection cue, not proof of editing.",
        ],
    }
