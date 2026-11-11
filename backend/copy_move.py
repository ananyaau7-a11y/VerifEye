from pathlib import Path
import cv2
import numpy as np


def detect_copy_move(
    image_path: str,
    output_path: str,
    min_matches: int = 12
) -> dict:
    """Find possible copy-move features using ORB matching."""

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Unable to read image for copy-move analysis.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(nfeatures=3000)
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    output = image.copy()
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if descriptors is None or len(keypoints) < 3:
        cv2.imwrite(str(destination), output)

        return {
            "available": False,
            "output_path": str(destination),
            "keypoints": len(keypoints),
            "possible_duplicate_matches": 0,
            "candidate_detected": False,
            "explanation": "Not enough distinctive features for matching."
        }

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

    # k=3 allows us to skip the self-match and compare
    # the best non-self candidate with the next candidate.
    raw_matches = matcher.knnMatch(
        descriptors,
        descriptors,
        k=3
    )

    good_matches = []

    for pair in raw_matches:
        candidates = [
            match for match in pair
            if match.queryIdx != match.trainIdx
        ]

        if len(candidates) < 2:
            continue

        first, second = candidates[:2]

        point_a = np.array(keypoints[first.queryIdx].pt)
        point_b = np.array(keypoints[first.trainIdx].pt)

        spatial_distance = np.linalg.norm(point_a - point_b)

        if spatial_distance < 30:
            continue

        if first.distance < 0.7 * second.distance:
            good_matches.append(first)

    for match in good_matches:
        point_a = tuple(
            np.round(keypoints[match.queryIdx].pt).astype(int)
        )
        point_b = tuple(
            np.round(keypoints[match.trainIdx].pt).astype(int)
        )

        cv2.circle(output, point_a, 5, (0, 255, 255), 2)
        cv2.circle(output, point_b, 5, (0, 0, 255), 2)
        cv2.line(output, point_a, point_b, (255, 255, 0), 1)

    if not cv2.imwrite(str(destination), output):
        raise ValueError("Unable to save copy-move visualization.")

    return {
        "available": True,
        "output_path": str(destination),
        "keypoints": len(keypoints),
        "possible_duplicate_matches": len(good_matches),
        "minimum_matches_reference": min_matches,
        "candidate_detected": len(good_matches) >= min_matches,
        "explanation": (
            "Spatially separated similar features were identified. "
            "This can occur in copy-move edits or naturally repetitive "
            "content. Manual inspection is required."
        )
    }