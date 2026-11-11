
from pathlib import Path
from uuid import uuid4
import logging
import shutil
import warnings

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from backend.enhanced_analysis import run_enhanced_analysis
from backend.similarity import compare_images
from backend.comparison_report import generate_comparison_report
from backend.ocr_comparison import compare_image_text


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

MAX_FILE_SIZE = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
CHUNK_SIZE = 1024 * 1024

ALLOWED_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifeye")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="VerifEye AI-Assisted Image Forensics API",
    description=(
        "An explainable image-analysis API that examines "
        "metadata, compression, noise, edges, possible "
        "copy-move signals, typography, visual differences "
        "and OCR text."
    ),
    version="2.4.0",
)

app.mount(
    "/files",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="files",
)


# =========================================================
# HOME AND HEALTH
# =========================================================

@app.get("/")
def home():
    return {
        "application": "VerifEye",
        "status": "running",
        "version": "2.4.0",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VerifEye API",
        "ocr_module": "available",
        "typography_module": "available",
        "risk_scoring": "available",
    }


# =========================================================
# IMAGE SAVE AND VALIDATION
# =========================================================

async def save_and_validate_image(
    upload: UploadFile,
    job_dir: Path,
    prefix: str,
):
    temporary_path = job_dir / f"{prefix}_upload"
    total_size = 0

    try:
        with temporary_path.open("wb") as buffer:
            while True:
                chunk = await upload.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Each image must be 15 MB or smaller.",
                    )

                buffer.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

        try:
            with warnings.catch_warnings():
                warnings.simplefilter(
                    "error",
                    Image.DecompressionBombWarning,
                )

                with Image.open(temporary_path) as image:
                    image_format = image.format
                    width, height = image.size

                    if image_format not in ALLOWED_FORMATS:
                        raise HTTPException(
                            status_code=415,
                            detail=(
                                "Only JPEG, PNG and WebP images "
                                "are supported."
                            ),
                        )

                    if width <= 0 or height <= 0:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid image dimensions.",
                        )

                    if width * height > MAX_IMAGE_PIXELS:
                        raise HTTPException(
                            status_code=413,
                            detail=(
                                "Image dimensions exceed the "
                                "40-megapixel limit."
                            ),
                        )

                    image.verify()

        except HTTPException:
            raise

        except (
            UnidentifiedImageError,
            OSError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded file is invalid, corrupted, "
                    "or unsafe to process."
                ),
            )

        final_path = job_dir / (
            prefix + ALLOWED_FORMATS[image_format]
        )

        temporary_path.rename(final_path)

        image_info = {
            "filename": upload.filename or final_path.name,
            "format": image_format,
            "width": width,
            "height": height,
            "dimensions": f"{width} x {height}",
            "file_size_bytes": total_size,
            "file_size_kb": round(total_size / 1024, 2),
        }

        return final_path, image_info

    finally:
        await upload.close()


# =========================================================
# SINGLE IMAGE VERIFICATION
# =========================================================

@app.post("/api/verify")
async def verify_image(
    file: UploadFile = File(...),
):
    job_id = str(uuid4())
    job_dir = OUTPUT_DIR / job_id

    job_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    try:
        safe_input_path, _ = await save_and_validate_image(
            file,
            job_dir,
            "original",
        )

        # Enhanced pipeline: original analysis + typography + score.
        result = run_enhanced_analysis(
            str(safe_input_path),
            str(job_dir),
        )

        result["job_id"] = job_id

        # Convert artifact filenames to accessible API URLs.
        artifacts = result.get("artifacts", {})

        for key, filename in artifacts.items():
            if filename:
                artifacts[key] = (
                    f"/files/{job_id}/{Path(str(filename)).name}"
                )

        result["artifacts"] = artifacts

        return result

    except HTTPException:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise

    except Exception:
        logger.exception(
            "Single image analysis failed for job %s",
            job_id,
        )

        shutil.rmtree(job_dir, ignore_errors=True)

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred during image "
                "analysis. Please try again."
            ),
        )


# =========================================================
# TWO IMAGE COMPARISON
# =========================================================

@app.post("/api/compare")
async def compare_two_images(
    first_file: UploadFile = File(...),
    second_file: UploadFile = File(...),
):
    job_id = str(uuid4())
    job_dir = OUTPUT_DIR / job_id

    job_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    try:
        # SAVE AND VALIDATE FIRST IMAGE
        first_path, first_info = await save_and_validate_image(
            first_file,
            job_dir,
            "first",
        )

        # SAVE AND VALIDATE SECOND IMAGE
        second_path, second_info = await save_and_validate_image(
            second_file,
            job_dir,
            "second",
        )

        # VISUAL IMAGE COMPARISON
        comparison = compare_images(
            str(first_path),
            str(second_path),
            str(job_dir),
        )

        # OCR TEXT COMPARISON
        try:
            ocr_result = compare_image_text(
                str(first_path),
                str(second_path),
            )

        except Exception:
            logger.exception(
                "OCR comparison failed for job %s",
                job_id,
            )

            ocr_result = {
                "available": False,
                "assessment": (
                    "OCR comparison could not be completed. "
                    "Visual comparison results remain available."
                ),
                "limitations": [
                    "OCR results are unavailable for this comparison."
                ],
            }

        comparison["ocr_comparison"] = ocr_result

        # GENERATE COMPARISON PDF
        report_path = generate_comparison_report(
            first_image=first_info,
            second_image=second_info,
            comparison=comparison,
            output_path=str(
                job_dir / "comparison_report.pdf"
            ),
        )

        # RESPONSE
        return {
            "job_id": job_id,
            "first_image": first_info,
            "second_image": second_info,
            "comparison": comparison,
            "artifacts": {
                "difference_heatmap": (
                    f"/files/{job_id}/"
                    f"{Path(comparison['difference_heatmap']).name}"
                ),
                "comparison_pdf": (
                    f"/files/{job_id}/"
                    f"{Path(report_path).name}"
                ),
            },
        }

    except HTTPException:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise

    except Exception:
        logger.exception(
            "Two-image comparison failed for job %s",
            job_id,
        )

        shutil.rmtree(job_dir, ignore_errors=True)

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred during image "
                "comparison or report generation."
            ),
        )
