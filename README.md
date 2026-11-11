# VerifEye — AI-Assisted Digital Image Forensics

VerifEye is an image-forensics prototype that examines digital images
for potentially suspicious characteristics using explainable image
analysis techniques.

Instead of claiming to determine authenticity with an arbitrary
percentage, VerifEye presents individual forensic observations
that users can inspect.

## Features

- Image metadata and EXIF extraction
- Error Level Analysis (JPEG images)
- Local noise residual visualization
- Edge detection and boundary visualization
- ORB-based copy-move feature matching
- Explainable forensic findings
- PDF forensic report generation
- FastAPI backend
- Streamlit dashboard
- JPEG, PNG and WebP upload support
- Unique analysis folders for uploaded images

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend API |
| Streamlit | Frontend dashboard |
| OpenCV | Image processing and feature matching |
| Pillow | Image loading and metadata |
| NumPy | Numerical operations |
| Scikit-image | Structural similarity |
| ReportLab | PDF report generation |

## Project Structure

```text
project1/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── metadata.py
│   ├── ela.py
│   ├── noise_analysis.py
│   ├── edge_analysis.py
│   ├── copy_move.py
│   ├── similarity.py
│   ├── evidence_engine.py
│   ├── analysis.py
│   └── report_gen.py
├── frontend/
│   ├── app.py
│   └── styles.py
├── tests/
│   ├── test_analysis.py
│   └── test_upload.py
├── samples/
│   ├── original/
│   └── manipulated/
├── output/
├── requirements.txt
├── .gitignore
└── README.md