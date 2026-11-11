# VerifEye — AI-Assisted Digital Image Forensics

VerifEye is an explainable digital image forensics prototype that analyzes images for potentially suspicious characteristics and helps users investigate possible signs of manipulation.

Instead of assigning an arbitrary authenticity percentage or claiming to conclusively identify fake images, VerifEye presents individual forensic observations, visual evidence, and comparison results that users can inspect.

**Live Demo:** [VerifEye Dashboard](https://verifeye-ai.streamlit.app/)  
**Backend API:** [VerifEye API](https://verifeye-xc6j.onrender.com)  
**API Documentation:** [Interactive API Docs](https://verifeye-xc6j.onrender.com/docs)  
**GitHub Repository:** [AnanyaAU7/VerifEye](https://github.com/ananyaau7-a11y/VerifEye)

---

## Features

### 1. Single Image Forensic Analysis

- **Metadata and EXIF Extraction** — Examines available image metadata.
- **Error Level Analysis (ELA)** — Highlights variations in JPEG compression levels.
- **Noise Residual Analysis** — Visualizes local noise characteristics.
- **Edge Detection** — Examines image boundaries and structural details.
- **Copy-Move Detection** — Uses ORB-based feature matching to identify potential duplicated regions.
- **Typography Analysis** — Examines text-related characteristics that may indicate inconsistencies.
- **Risk Scoring** — Combines forensic observations into an interpretable risk assessment.
- **Explainable Findings** — Presents individual forensic observations rather than relying only on an unexplained score.
- **PDF Reports** — Generates downloadable forensic analysis reports.

### 2. Image Comparison

- Upload and compare two images.
- Structural Similarity Index (SSIM) analysis.
- Pixel-level difference analysis.
- Changed pixel count and percentage.
- Difference heatmap visualization.
- Candidate changed-region identification.
- Visual highlighting of changed regions and close-up crops.
- OCR-based text comparison.
- Downloadable comparison reports in PDF format.

### 3. Dashboard

- Interactive Streamlit interface.
- Support for JPEG, PNG, and WebP images.
- Separate analysis folders for uploaded images.
- Visual presentation of forensic results and comparison evidence.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend API development |
| Streamlit | Interactive frontend dashboard |
| OpenCV | Image processing, edge detection, and feature matching |
| Pillow | Image loading and metadata extraction |
| NumPy | Numerical and pixel-level operations |
| Scikit-image | Structural similarity analysis |
| Pytesseract | OCR-based text extraction |
| ReportLab | PDF report generation |

---

## System Architecture

VerifEye uses a separate frontend and backend architecture.

```text
                 USER
                   |
                   v
          STREAMLIT FRONTEND
                   |
                   v
             FASTAPI BACKEND
                   |
          +--------+--------+
          |                 |
          v                 v
    SINGLE IMAGE       IMAGE COMPARISON
      ANALYSIS              ANALYSIS
          |                 |
          v                 v
     FORENSIC           SIMILARITY &
     ANALYSIS           DIFFERENCE
     MODULES             ANALYSIS
          |                 |
          +--------+--------+
                   |
                   v
           RESULTS & VISUALS
                   |
                   v
              PDF REPORTS
```

### Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API root |
| GET | `/api/health` | Backend health check |
| POST | `/api/verify` | Single-image forensic analysis |
| POST | `/api/compare` | Two-image comparison |

---

## Project Structure

```text
VerifEye/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── analysis.py
│   ├── enhanced_analysis.py
│   ├── metadata.py
│   ├── ela.py
│   ├── noise_analysis.py
│   ├── edge_analysis.py
│   ├── copy_move.py
│   ├── similarity.py
│   ├── evidence_engine.py
│   ├── risk_scoring.py
│   ├── typography_analysis.py
│   ├── ocr_comparison.py
│   ├── report_gen.py
│   └── comparison_report.py
│
├── frontend/
│   ├── app.py
│   └── styles.py
│
├── tests/
│   ├── test_analysis.py
│   ├── test_similarity.py
│   └── test_upload.py
│
├── Dockerfile
├── requirements.txt
├── requirements-backend.txt
├── .gitignore
└── README.md
```

---

## Installation and Local Setup

### Prerequisites

- Python 3.10 or later
- Git
- Tesseract OCR installed and accessible if using OCR functionality

### 1. Clone the Repository

```bash
git clone https://github.com/ananyaau7-a11y/VerifEye.git
cd VerifEye
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Backend

Open a terminal in the project root:

```bash
uvicorn backend.main:app --reload
```

The backend will run at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 5. Start the Frontend

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run frontend/app.py
```

**Note:** The deployed frontend is configured to communicate with the public Render backend. For a fully local setup, configure the frontend API URL to point to `http://127.0.0.1:8000`.

---

## Testing

Run the automated test suite from the project root:

```bash
python -m pytest -v
```

The project test suite passed **13 tests** in the development environment.

---

## Deployment

VerifEye is deployed using free-tier hosting services.

| Component | Platform |
|---|---|
| Frontend | Streamlit Community Cloud |
| Backend | Render |
| Backend Runtime | Docker |
| Source Code | GitHub |

**Deployment Links:**

- [Live Frontend](https://verifeye-ai.streamlit.app/)
- [Backend Service](https://verifeye-xc6j.onrender.com)
- [API Documentation](https://verifeye-xc6j.onrender.com/docs)

---

## Limitations and Responsible Use

VerifEye is an experimental forensic analysis tool, not a definitive image-authentication system.

- Forensic indicators can produce false positives and false negatives.
- Error Level Analysis is primarily applicable to JPEG images and must be interpreted carefully.
- Metadata may be absent, modified, or stripped during image processing.
- Copy-move feature matching identifies potential similarities, not conclusive manipulation.
- Noise, compression, resizing, and image transformations can affect analysis results.
- Risk scores are indicators based on implemented analysis techniques, not probabilities that an image is fake.
- Results should be interpreted alongside the original image, its source, and other available evidence.

**VerifEye is intended to assist human investigation, not replace expert forensic judgment.**

---

## Future Improvements

- More advanced image manipulation detection techniques.
- Improved localization and interpretation of suspicious regions.
- Expanded forensic analysis methods.
- Performance and memory optimization.
- Additional testing across diverse image formats and manipulation scenarios.

---

## Author

**Ananya A.U.**  
B.E. Computer Science and Engineering

GitHub: [ananyaau7-a11y](https://github.com/ananyaau7-a11y)

---

*VerifEye — Making digital image analysis more transparent and explainable.*