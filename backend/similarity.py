
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity


def compare_images(first_image_path: str, second_image_path: str, output_dir: str) -> dict:
    """
    Compare two images using SSIM and pixel differences.
    Generates a difference heatmap and identifies larger changed regions.

    The result does not establish which image is authentic.
    """
    try:
        with Image.open(first_image_path) as first:
            image_a = first.convert("RGB")

        with Image.open(second_image_path) as second:
            image_b = second.convert("RGB")

        original_size_a = image_a.size
        original_size_b = image_b.size
        same_dimensions = original_size_a == original_size_b

        if not same_dimensions:
            image_b = image_b.resize(
                original_size_a,
                Image.Resampling.LANCZOS
            )

        array_a = np.asarray(image_a)
        array_b = np.asarray(image_b)

        score, similarity_map = structural_similarity(
            array_a,
            array_b,
            channel_axis=2,
            full=True,
            data_range=255
        )

        difference = np.abs(
            array_a.astype(np.int16) - array_b.astype(np.int16)
        )

        difference_map = np.mean(difference, axis=2)

        threshold = 25
        changed_mask = (difference_map > threshold).astype(np.uint8)

        total_pixels = int(changed_mask.size)
        changed_pixels = int(np.count_nonzero(changed_mask))

        changed_percentage = (
            changed_pixels / total_pixels * 100
            if total_pixels else 0
        )

        # Amplified difference heatmap.
        heatmap = np.clip(
            difference_map * 4,
            0,
            255
        ).astype(np.uint8)

        heatmap_color = cv2.applyColorMap(
            heatmap,
            cv2.COLORMAP_JET
        )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        heatmap_path = output_path / "difference_heatmap.png"

        cv2.imwrite(
            str(heatmap_path),
            heatmap_color
        )

        # Find connected changed regions.
        # Very small regions are ignored to reduce noise.
        count, labels, stats, centroids = cv2.connectedComponentsWithStats(
            changed_mask,
            connectivity=8
        )

        changed_regions = []

        min_region_area = max(
            20,
            int(total_pixels * 0.0001)
        )

        for index in range(1, count):
            x, y, width, height, area = stats[index]

            if area < min_region_area:
                continue

            changed_regions.append({
                "x": int(x),
                "y": int(y),
                "width": int(width),
                "height": int(height),
                "area_pixels": int(area),
                "center": {
                    "x": round(float(centroids[index][0]), 2),
                    "y": round(float(centroids[index][1]), 2)
                }
            })

        changed_regions.sort(
            key=lambda region: region["area_pixels"],
            reverse=True
        )

        # Keep the response manageable.
        changed_regions = changed_regions[:30]

        return {
            "ssim_score": round(float(score), 5),
            "similarity_percentage": round(float(score * 100), 2),
            "same_dimensions_originally": same_dimensions,
            "first_image_dimensions": list(original_size_a),
            "second_image_dimensions": list(original_size_b),
            "comparison_dimensions": list(original_size_a),
            "changed_pixel_percentage": round(
                float(changed_percentage), 2
            ),
            "changed_pixel_count": changed_pixels,
            "total_pixel_count": total_pixels,
            "changed_region_count": len(changed_regions),
            "changed_regions": changed_regions,
            "difference_threshold": threshold,
            "difference_heatmap": heatmap_path.name,
            "explanation": (
                "SSIM measures structural similarity. Pixel difference "
                "analysis highlights areas that differ after the second "
                "image is resized to the first image's dimensions, if "
                "necessary. Changed regions are algorithmic candidates, "
                "not confirmed edits. These measurements do not establish "
                "which image is authentic or whether differences were "
                "intentional."
            )
        }

    except Exception as error:
        raise ValueError(
            f"Image comparison failed: {error}"
        ) from error
