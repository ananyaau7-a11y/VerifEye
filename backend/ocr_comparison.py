
import re
import difflib
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps
from pytesseract import Output


# Explicit path ensures the backend can find Tesseract even if
# its terminal was opened before the PATH was updated.
TESSERACT_EXE = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if TESSERACT_EXE.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)


def _normalise_text(text: str) -> str:
    """Normalise whitespace and case for comparison."""
    return re.sub(r"\s+", " ", text).strip().casefold()


def extract_image_text(image_path: str) -> dict:
    """Extract text and OCR confidence from an image."""
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")

        # Improve basic contrast without changing the source file.
        processed = ImageOps.autocontrast(
            ImageOps.grayscale(image)
        )

        data = pytesseract.image_to_data(
            processed,
            lang="eng",
            config="--oem 3 --psm 6",
            output_type=Output.DICT
        )

        words = []
        confidences = []

        for word, confidence in zip(data["text"], data["conf"]):
            word = word.strip()

            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                continue

            if word and confidence >= 0:
                words.append(word)
                confidences.append(confidence)

        extracted_text = " ".join(words).strip()

        average_confidence = (
            round(sum(confidences) / len(confidences), 2)
            if confidences else 0.0
        )

        return {
            "text": extracted_text,
            "average_confidence": average_confidence,
            "words_detected": len(words),
            "extraction_status": (
                "Text detected" if extracted_text
                else "No readable text detected"
            )
        }

    except pytesseract.TesseractNotFoundError as error:
        raise RuntimeError(
            "Tesseract OCR executable was not found. "
            "Check the Tesseract installation."
        ) from error

    except Exception as error:
        raise RuntimeError(
            f"OCR extraction failed: {error}"
        ) from error


def compare_image_text(
    first_image_path: str,
    second_image_path: str
) -> dict:
    """
    Extract and compare text from two images.

    Added, removed and modified entries are candidate textual
    differences, not proof of image manipulation.
    """
    first = extract_image_text(first_image_path)
    second = extract_image_text(second_image_path)

    first_lines = [
        line.strip()
        for line in first["text"].splitlines()
        if line.strip()
    ]
    second_lines = [
        line.strip()
        for line in second["text"].splitlines()
        if line.strip()
    ]

    # Tesseract's word output is joined into one line, so compare
    # normalised word sequences to identify textual changes.
    first_words = first["text"].split()
    second_words = second["text"].split()

    matcher = difflib.SequenceMatcher(
        None,
        [_normalise_text(word) for word in first_words],
        [_normalise_text(word) for word in second_words],
        autojunk=False
    )

    added = []
    removed = []
    modified = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old_words = first_words[i1:i2]
        new_words = second_words[j1:j2]

        if tag == "insert":
            added.extend(new_words)

        elif tag == "delete":
            removed.extend(old_words)

        elif tag == "replace":
            modified.append({
                "first_image_text": " ".join(old_words),
                "second_image_text": " ".join(new_words)
            })

    same_text = (
        _normalise_text(first["text"])
        == _normalise_text(second["text"])
    )

    return {
        "available": True,
        "same_text": same_text,
        "first_image": first,
        "second_image": second,
        "added_text": added,
        "removed_text": removed,
        "modified_text": modified,
        "added_word_count": len(added),
        "removed_word_count": len(removed),
        "modified_segment_count": len(modified),
        "assessment": (
            "No textual differences were detected by OCR."
            if same_text else
            "Potential textual differences were detected. "
            "Review the extracted text and original images."
        ),
        "limitations": [
            "OCR may misread digits, symbols, small text or low-quality images.",
            "Text order and layout differences can affect comparison.",
            "A detected text difference does not prove manipulation.",
            "OCR cannot establish which image is authentic.",
            "Human review of the original images is necessary."
        ]
    }
