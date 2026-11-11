
import streamlit as st
import requests
from PIL import Image, ImageDraw
from io import BytesIO

# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="VerifEye | Digital Image Forensics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# DESIGN
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0b1120;
    color: #e5e7eb;
}

.main .block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif;
    color: #f8fafc;
}

p, label, span {
    color: #cbd5e1;
}

[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263247;
}

.hero {
    background: linear-gradient(120deg, #14243c, #172554);
    border: 1px solid #2d4568;
    border-radius: 18px;
    padding: 30px;
    margin: 12px 0 24px 0;
}

.hero-label {
    color: #7dd3fc;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 8px 0;
}

.hero-description {
    color: #cbd5e1;
    font-size: 1rem;
    max-width: 750px;
    line-height: 1.7;
}

.section-card {
    background: #131d2e;
    border: 1px solid #29364d;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
}

.status-pill {
    display: inline-block;
    background: #12352f;
    color: #86efac;
    border: 1px solid #276749;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}

.status-offline {
    display: inline-block;
    background: #3b2028;
    color: #fda4af;
    border: 1px solid #7f1d1d;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background: #151f32;
    border: 1px solid #29364d;
    padding: 16px;
    border-radius: 12px;
}

div[data-testid="stMetricLabel"] {
    color: #94a3b8;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc;
}

.stButton > button {
    background: linear-gradient(90deg, #2563eb, #4f46e5);
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    min-height: 44px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    border: 1px solid #93c5fd;
    color: white;
}

.stDownloadButton > button {
    background: #172b45;
    color: #bfdbfe;
    border: 1px solid #31547d;
    border-radius: 9px;
    min-height: 42px;
}

[data-testid="stFileUploader"] {
    background: #131d2e;
    border: 1px dashed #40516d;
    border-radius: 12px;
    padding: 12px;
}

div[data-testid="stExpander"] {
    background: #131d2e;
    border: 1px solid #29364d;
    border-radius: 10px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: 1px solid #29364d;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 12px 18px;
}

.stTabs [aria-selected="true"] {
    background: #172b45 !important;
    color: #93c5fd !important;
}

.small-muted {
    color: #94a3b8;
    font-size: 0.85rem;
}

.result-heading {
    color: #93c5fd;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.15rem;
    margin-top: 12px;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

hr {
    border-color: #29364d;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def api_request(method, endpoint, **kwargs):
    kwargs.setdefault("timeout", 180)

    response = requests.request(
        method,
        f"{API_URL}{endpoint}",
        **kwargs
    )

    response.raise_for_status()
    return response


def display_artifact(title, artifact_path):
    if not artifact_path:
        st.info(f"{title} is unavailable.")
        return

    try:
        response = api_request(
            "GET",
            artifact_path,
            timeout=30
        )

        st.image(
            response.content,
            caption=title,
            use_container_width=True
        )

    except requests.RequestException:
        st.warning(f"Could not load {title}.")


def download_pdf(label, artifact_path, filename, key):
    if not artifact_path:
        st.warning("PDF report is unavailable.")
        return

    try:
        response = api_request(
            "GET",
            artifact_path,
            timeout=30
        )

        st.download_button(
            label=label,
            data=response.content,
            file_name=filename,
            mime="application/pdf",
            key=key,
            use_container_width=True
        )

    except requests.RequestException:
        st.error("Could not retrieve the PDF report.")


def show_findings(findings):
    if not findings:
        st.info("No findings were returned.")
        return

    for finding in findings:
        method = finding.get("method", "Analysis")
        severity = finding.get("severity", "Informational")
        observation = finding.get("observation", "")

        with st.expander(f"{method} — {severity}"):
            st.write(observation)


def show_limitations(limitations):
    if limitations:
        for item in limitations:
            st.write(f"• {item}")
    else:
        st.write("No additional limitations were returned.")


def create_region_visuals(first_bytes, second_bytes, region):
    first_image = Image.open(
        BytesIO(first_bytes)
    ).convert("RGB")

    second_image = Image.open(
        BytesIO(second_bytes)
    ).convert("RGB")

    original_second_size = second_image.size

    if second_image.size != first_image.size:
        second_image = second_image.resize(
            first_image.size,
            Image.Resampling.LANCZOS
        )

    x = int(region.get("x", 0))
    y = int(region.get("y", 0))
    width = int(region.get("width", 0))
    height = int(region.get("height", 0))

    left = max(0, x)
    top = max(0, y)
    right = min(first_image.width, x + width)
    bottom = min(first_image.height, y + height)

    if right <= left or bottom <= top:
        return None

    box = (left, top, right, bottom)

    first_crop = first_image.crop(box)
    second_crop = second_image.crop(box)

    first_highlight = first_image.copy()
    second_highlight = second_image.copy()

    line_width = max(
        3,
        min(first_image.width, first_image.height) // 250
    )

    for image in (first_highlight, second_highlight):
        draw = ImageDraw.Draw(image)

        draw.rectangle(
            box,
            outline="#ff3158",
            width=line_width
        )

    return {
        "first_crop": first_crop,
        "second_crop": second_crop,
        "first_highlight": first_highlight,
        "second_highlight": second_highlight,
        "original_second_size": original_second_size
    }


def show_changed_region(index, region, first_bytes, second_bytes):
    visuals = create_region_visuals(
        first_bytes,
        second_bytes,
        region
    )

    if visuals is None:
        st.warning(
            f"Could not generate the visual for region {index}."
        )
        return

    st.markdown(f"### Changed Region {index}")

    st.caption(
        "The highlighted area identifies a candidate difference. "
        "Inspect the corresponding close-up images below."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            visuals["first_highlight"],
            caption="Image 1 — Highlighted location",
            use_container_width=True
        )

    with col2:
        st.image(
            visuals["second_highlight"],
            caption="Image 2 — Highlighted location",
            use_container_width=True
        )

    st.markdown("**Close-up comparison**")

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            visuals["first_crop"],
            caption="Image 1 — Detected area",
            use_container_width=True
        )

    with col2:
        st.image(
            visuals["second_crop"],
            caption="Image 2 — Corresponding area",
            use_container_width=True
        )

    if (
        visuals["original_second_size"]
        != visuals["first_highlight"].size
    ):
        st.caption(
            "Image 2 was resized for coordinate alignment "
            "during this visual comparison."
        )

    area = region.get("area")

    if area is not None:
        st.caption(f"Approximate detected area: {area:,} pixels")


def show_ocr_comparison(ocr):
    if not ocr:
        st.info("Text comparison information is unavailable.")
        return

    if not ocr.get("available", False):
        st.info(
            ocr.get(
                "error",
                "Text comparison could not be completed."
            )
        )
        return

    st.subheader("Text Comparison")

    st.info(
        ocr.get(
            "assessment",
            "Text extraction completed. Review the results below."
        )
    )

    first = ocr.get("first_image", {})
    second = ocr.get("second_image", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Image 1 extracted text**")

        st.metric(
            "Words detected",
            first.get("words_detected", "N/A")
        )

        st.text_area(
            "Text from Image 1",
            value=first.get("text", ""),
            height=180,
            key="ocr_first_text",
            disabled=True
        )

    with col2:
        st.markdown("**Image 2 extracted text**")

        st.metric(
            "Words detected",
            second.get("words_detected", "N/A")
        )

        st.text_area(
            "Text from Image 2",
            value=second.get("text", ""),
            height=180,
            key="ocr_second_text",
            disabled=True
        )

    st.markdown("#### Detected text changes")

    added = ocr.get("added_text", [])
    removed = ocr.get("removed_text", [])
    modified = ocr.get("modified_text", [])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Added**")

        if added:
            for item in added:
                st.success(str(item))
        else:
            st.write("None detected")

    with col2:
        st.markdown("**Removed**")

        if removed:
            for item in removed:
                st.error(str(item))
        else:
            st.write("None detected")

    with col3:
        st.markdown("**Modified**")

        if modified:
            for item in modified:
                if isinstance(item, dict):
                    st.warning(
                        f"Image 1: {item.get('first_image_text', '')}\n\n"
                        f"Image 2: {item.get('second_image_text', '')}"
                    )
                else:
                    st.warning(str(item))
        else:
            st.write("None detected")

    limitations = ocr.get("limitations", [])

    if limitations:
        with st.expander("Text extraction limitations"):
            show_limitations(limitations)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("# 🛡️ VerifEye")

    st.caption("AI-Assisted Digital Image Forensics")

    st.markdown("---")

    st.markdown("### Your workspace")

    st.write("🔍 Single image inspection")
    st.write("⚖️ Two-image comparison")
    st.write("📄 Downloadable forensic reports")
    st.write("📖 Analysis guide")

    st.markdown("---")

    try:
        api_request(
            "GET",
            "/api/health",
            timeout=5
        )

        st.markdown(
            "<span class='status-pill'>● Service Ready</span>",
            unsafe_allow_html=True
        )

    except requests.RequestException:
        st.markdown(
            "<span class='status-offline'>● Service Unavailable</span>",
            unsafe_allow_html=True
        )

        st.caption(
            "The analysis service is currently unavailable."
        )

    st.markdown("---")

    st.caption("VerifEye | Experimental Prototype")


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-label">DIGITAL IMAGE FORENSICS</div>
    <div class="hero-title">VerifEye</div>
    <div class="hero-description">
        Examine image characteristics, investigate visual differences,
        and review potential manipulation indicators through one
        unified workspace.
    </div>
</div>
""", unsafe_allow_html=True)

try:
    api_request("GET", "/api/health", timeout=5)
    st.markdown(
        "<span class='status-pill'>● Analysis service ready</span>",
        unsafe_allow_html=True
    )
except requests.RequestException:
    st.markdown(
        "<span class='status-offline'>● Analysis service unavailable</span>",
        unsafe_allow_html=True
    )
    st.warning(
        "The backend service is not reachable. Start the FastAPI "
        "server before running an analysis."
    )

st.markdown("")

single_tab, comparison_tab, guide_tab = st.tabs([
    "🔍  Single Image Analysis",
    "⚖️  Compare Images",
    "📖  How to Use"
])


# =========================================================
# TAB 1: SINGLE IMAGE ANALYSIS
# =========================================================

with single_tab:

    st.header("Single Image Inspection")

    st.write(
        "Upload an image to examine its metadata, visual characteristics "
        "and potential forensic indicators."
    )

    uploaded_file = st.file_uploader(
        "Choose an image to inspect",
        type=["jpg", "jpeg", "png", "webp"],
        key="single_image_upload"
    )

    if uploaded_file is not None:

        uploaded_bytes = uploaded_file.getvalue()

        col1, col2 = st.columns([1.4, 1])

        with col1:
            st.image(
                uploaded_bytes,
                caption=uploaded_file.name,
                use_container_width=True
            )

        with col2:
            st.markdown("### Uploaded Image")

            st.write(f"**Filename:** {uploaded_file.name}")

            st.write(
                f"**File size:** {len(uploaded_bytes) / 1024:.2f} KB"
            )

            st.caption(
                "Supported formats: JPG, JPEG, PNG and WEBP."
            )

        if st.button(
            "Run Forensic Analysis",
            type="primary",
            use_container_width=True,
            key="run_single_analysis"
        ):

            with st.spinner("Examining image evidence..."):

                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_bytes,
                            uploaded_file.type
                        )
                    }

                    response = api_request(
                        "POST",
                        "/api/verify",
                        files=files
                    )

                    st.session_state["verification_result"] = (
                        response.json()
                    )

                    st.success("Image analysis completed.")

                except requests.RequestException as error:
                    st.error(f"Analysis request failed: {error}")

                except ValueError as error:
                    st.error(f"Invalid server response: {error}")

    result = st.session_state.get("verification_result")

    if result is not None:

        metadata = result.get("metadata", {})
        ela = result.get("ela_analysis", {})
        noise = result.get("noise_analysis", {})
        edges = result.get("edge_analysis", {})
        copy_move = result.get("copy_move_analysis", {})
        typography = result.get("typography_analysis", {})
        evidence = result.get("evidence", {})
        risk = result.get("risk_score", {})
        artifacts = result.get("artifacts", {})

        st.markdown("---")
        st.header("Analysis Results")

        # -------------------------------------------------
        # REVIEW PRIORITY
        # -------------------------------------------------

        st.subheader("Review Priority Assessment")

        if risk:

            score = risk.get("score", 0)
            level = risk.get("level", "Not available")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.metric(
                    "Review Priority Score",
                    f"{score}/100"
                )

            with col2:
                st.markdown(f"### {level}")

                st.write(
                    risk.get(
                        "interpretation",
                        "Review the findings below."
                    )
                )

            reasons = risk.get("reasons", [])

            if reasons:
                st.markdown("**Indicators contributing to this score**")

                for reason in reasons:
                    st.write(f"• {reason}")

        else:
            st.info("Review priority score is unavailable.")

        st.caption(
            "This experimental score indicates review priority. "
            "It is not a probability that an image has been manipulated."
        )

        # -------------------------------------------------
        # EVIDENCE SUMMARY
        # -------------------------------------------------

        st.markdown("---")
        st.subheader("Evidence Summary")

        review_count = evidence.get("review_signal_count", 0)
        inconclusive_count = evidence.get("inconclusive_count", 0)
        findings = evidence.get("findings", [])

        if review_count > 0:

            st.warning(
                "Potential indicators require closer inspection."
            )

            st.write(
                "One or more analysis methods identified patterns "
                "that deserve manual review. This does not establish "
                "that the image was manipulated."
            )

        elif inconclusive_count > 0:

            st.info(
                "Some analysis methods produced inconclusive results."
            )

        else:

            st.success(
                "No strong review indicators were returned "
                "by the current checks."
            )

        st.info(
            evidence.get(
                "summary",
                "Analysis completed. Review the individual findings."
            )
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Review Signals", review_count)

        with col2:
            st.metric("Inconclusive Checks", inconclusive_count)

        # -------------------------------------------------
        # IMAGE OVERVIEW
        # -------------------------------------------------

        st.markdown("---")
        st.subheader("Image Overview")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Format",
                metadata.get("format", "Unknown")
            )

        with c2:
            st.metric(
                "Dimensions",
                metadata.get("dimensions", "Unknown")
            )

        with c3:
            st.metric(
                "File Size",
                f"{metadata.get('file_size_kb', 0)} KB"
            )

        # -------------------------------------------------
        # VISUAL ANALYSIS
        # -------------------------------------------------

        st.markdown("---")
        st.header("Forensic Visualizations")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Error Level Analysis")

            st.caption(ela.get("explanation", ""))

            if ela.get("available", True):
                display_artifact(
                    "ELA Heatmap",
                    artifacts.get("ela_heatmap")
                )
            else:
                st.info(
                    "ELA is unavailable for this image format."
                )

        with col2:
            st.subheader("Noise Residual Analysis")

            st.caption(noise.get("explanation", ""))

            display_artifact(
                "Noise Map",
                artifacts.get("noise_map")
            )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Edge Analysis")

            st.caption(edges.get("explanation", ""))

            display_artifact(
                "Edge Map",
                artifacts.get("edge_map")
            )

        with col2:
            st.subheader("Copy-Move Analysis")

            st.caption(copy_move.get("explanation", ""))

            display_artifact(
                "Copy-Move Matches",
                artifacts.get("copy_move_matches")
            )

        # -------------------------------------------------
        # TYPOGRAPHY
        # -------------------------------------------------

        st.markdown("---")
        st.subheader("Typography Analysis")

        if typography:

            if typography.get("available", False):

                st.write(
                    typography.get(
                        "observation",
                        "Typography analysis completed."
                    )
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Text-like Components",
                        typography.get("component_count", "N/A")
                    )

                with col2:
                    st.metric(
                        "Text Rows",
                        typography.get("text_row_count", "N/A")
                    )

                display_artifact(
                    "Typography Analysis Overlay",
                    artifacts.get("typography_overlay")
                )

                for flag in typography.get("flags", []):
                    st.warning(str(flag))

            else:
                st.info(
                    typography.get(
                        "reason",
                        typography.get(
                            "status",
                            "Typography analysis was inconclusive."
                        )
                    )
                )

        else:
            st.info("Typography analysis is unavailable.")

        st.caption(
            "Typography checks are preliminary image-processing "
            "heuristics. They do not identify exact fonts or prove editing."
        )

        # -------------------------------------------------
        # FINDINGS
        # -------------------------------------------------

        st.markdown("---")
        st.header("Forensic Findings")

        show_findings(findings)

        # -------------------------------------------------
        # METADATA
        # -------------------------------------------------

        with st.expander("View Image Metadata"):
            st.json(metadata)

        with st.expander("Methodology and Limitations"):

            show_limitations(
                evidence.get("limitations", [])
            )

            st.write(
                "ELA, noise, edge, copy-move and typography indicators "
                "can produce false positives. Interpret them together "
                "and review the original evidence."
            )

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        st.markdown("---")
        st.subheader("Forensic Report")

        st.write(
            "Generate a downloadable report containing the "
            "image analysis findings."
        )

        download_pdf(
            "Download Forensic PDF Report",
            artifacts.get("pdf_report"),
            "VerifEye_Forensic_Report.pdf",
            "download_single_report"
        )


# =========================================================
# TAB 2: TWO-IMAGE COMPARISON
# =========================================================

with comparison_tab:

    st.header("Compare Two Images")

    st.write(
        "Compare two images to examine structural similarity, "
        "pixel differences, changed regions and text changes."
    )

    # -----------------------------------------------------
    # UPLOAD
    # -----------------------------------------------------

    upload_col1, upload_col2 = st.columns(2)

    with upload_col1:
        first_compare_file = st.file_uploader(
            "Upload Image 1",
            type=["jpg", "jpeg", "png", "webp"],
            key="first_comparison_image"
        )

    with upload_col2:
        second_compare_file = st.file_uploader(
            "Upload Image 2",
            type=["jpg", "jpeg", "png", "webp"],
            key="second_comparison_image"
        )

    first_bytes = (
        first_compare_file.getvalue()
        if first_compare_file is not None
        else None
    )

    second_bytes = (
        second_compare_file.getvalue()
        if second_compare_file is not None
        else None
    )

    # -----------------------------------------------------
    # PREVIEWS
    # -----------------------------------------------------

    preview1, preview2 = st.columns(2)

    with preview1:
        if first_bytes:
            st.image(
                first_bytes,
                caption="Image 1",
                use_container_width=True
            )

    with preview2:
        if second_bytes:
            st.image(
                second_bytes,
                caption="Image 2",
                use_container_width=True
            )

    # -----------------------------------------------------
    # RUN COMPARISON
    # -----------------------------------------------------

    if st.button(
        "Compare Images",
        type="primary",
        use_container_width=True,
        key="compare_images_button"
    ):

        if first_compare_file is None or second_compare_file is None:

            st.warning(
                "Please upload both images before comparing."
            )

        else:

            with st.spinner(
                "Comparing images and identifying visual differences..."
            ):

                try:
                    comparison_files = {
                        "first_file": (
                            first_compare_file.name,
                            first_bytes,
                            first_compare_file.type
                        ),
                        "second_file": (
                            second_compare_file.name,
                            second_bytes,
                            second_compare_file.type
                        )
                    }

                    response = api_request(
                        "POST",
                        "/api/compare",
                        files=comparison_files
                    )

                    st.session_state["comparison_result"] = (
                        response.json()
                    )

                    st.session_state["comparison_first_bytes"] = (
                        first_bytes
                    )

                    st.session_state["comparison_second_bytes"] = (
                        second_bytes
                    )

                    st.success("Image comparison completed.")

                except requests.RequestException as error:
                    st.error(
                        f"Comparison request failed: {error}"
                    )

                except ValueError as error:
                    st.error(
                        f"Invalid server response: {error}"
                    )

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    comparison_result = st.session_state.get(
        "comparison_result"
    )

    if comparison_result is not None:

        comparison = comparison_result.get(
            "comparison", {}
        )

        comparison_artifacts = comparison_result.get(
            "artifacts", {}
        )

        saved_first_bytes = st.session_state.get(
            "comparison_first_bytes"
        )

        saved_second_bytes = st.session_state.get(
            "comparison_second_bytes"
        )

        st.markdown("---")
        st.header("Comparison Results")

        # -------------------------------------------------
        # METRICS
        # -------------------------------------------------

        similarity = comparison.get(
            "similarity_percentage", 0
        )

        changed_pixels = comparison.get(
            "changed_pixel_percentage", 0
        )

        changed_regions = comparison.get(
            "changed_regions", []
        )

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric(
                "Structural Similarity",
                f"{similarity}%"
            )

        with metric2:
            st.metric(
                "Changed Pixels",
                f"{changed_pixels}%"
            )

        with metric3:
            st.metric(
                "Changed Regions",
                comparison.get(
                    "changed_region_count",
                    len(changed_regions)
                )
            )

        # -------------------------------------------------
        # EXPLANATION
        # -------------------------------------------------

        st.markdown("---")
        st.subheader("Comparison Summary")

        st.info(
            comparison.get(
                "explanation",
                "The comparison identifies structural and "
                "pixel-level differences between the images."
            )
        )

        st.caption(
            "A detected difference does not establish which "
            "image is authentic or original."
        )

        # -------------------------------------------------
        # DIFFERENCE HEATMAP
        # -------------------------------------------------

        st.markdown("---")
        st.subheader("Difference Heatmap")

        heatmap_path = comparison_artifacts.get(
            "difference_heatmap"
        )

        if heatmap_path:
            display_artifact(
                "Highlighted Visual Differences",
                heatmap_path
            )
        else:
            st.info("Difference heatmap is unavailable.")

        # -------------------------------------------------
        # CHANGED REGION VIEWER
        # -------------------------------------------------

        st.markdown("---")
        st.header("Visual Changed Region Analysis")

        if (
            changed_regions
            and saved_first_bytes
            and saved_second_bytes
        ):

            st.write(
                f"{len(changed_regions)} candidate changed region(s) "
                "were identified. Expand a region to inspect its "
                "highlighted location and close-up comparison."
            )

            for index, region in enumerate(
                changed_regions,
                start=1
            ):

                with st.expander(
                    f"Inspect Changed Region {index}",
                    expanded=(index == 1)
                ):

                    show_changed_region(
                        index,
                        region,
                        saved_first_bytes,
                        saved_second_bytes
                    )

        else:
            st.info(
                "No significant changed regions were detected, "
                "or visual region data is unavailable."
            )

        # -------------------------------------------------
        # OCR
        # -------------------------------------------------

        st.markdown("---")

        ocr_comparison = comparison.get(
            "ocr_comparison", {}
        )

        show_ocr_comparison(ocr_comparison)

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        st.markdown("---")
        st.subheader("Comparison Report")

        st.write(
            "Download a report containing the comparison results "
            "and available forensic findings."
        )

        download_pdf(
            "Download Comparison PDF Report",
            comparison_artifacts.get("comparison_pdf"),
            "VerifEye_Comparison_Report.pdf",
            "download_comparison_report"
        )


# =========================================================
# TAB 3: HOW TO USE
# =========================================================

with guide_tab:

    st.header("How to Use VerifEye")

    st.write(
        "A quick guide to the analysis workflow and the meaning "
        "of the results."
    )

    st.markdown("---")

    st.subheader("1. Single Image Analysis")

    st.markdown("""
    1. Open **Single Image Analysis**.
    2. Upload a JPG, JPEG, PNG or WEBP image.
    3. Click **Run Forensic Analysis**.
    4. Review the review-priority assessment and evidence summary.
    5. Inspect the forensic visualizations.
    6. Expand individual findings to understand the observations.
    7. Download the forensic PDF report if required.
    """)

    st.subheader("2. Compare Two Images")

    st.markdown("""
    1. Open **Compare Images**.
    2. Upload the first image.
    3. Upload the second image.
    4. Click **Compare Images**.
    5. Review structural similarity and changed-pixel metrics.
    6. Inspect the difference heatmap.
    7. Expand each changed region to see its highlighted location
       and corresponding close-up images.
    8. Review extracted text differences.
    9. Download the comparison PDF report.
    """)

    st.markdown("---")
    st.subheader("Understanding the Analysis")

    with st.expander("EXIF Metadata"):
        st.write(
            "Displays available image metadata, such as format, "
            "dimensions, file size and camera information when present. "
            "Missing metadata does not prove manipulation."
        )

    with st.expander("Error Level Analysis"):
        st.write(
            "Examines differences in JPEG recompression error. "
            "Unusual areas may deserve inspection, but compression, "
            "saving history and image content can also affect ELA."
        )

    with st.expander("Noise Residual Analysis"):
        st.write(
            "Examines local noise characteristics. Different noise "
            "patterns may indicate areas worth reviewing, but natural "
            "textures and image processing can also produce variation."
        )

    with st.expander("Edge Analysis"):
        st.write(
            "Highlights image boundaries and structural edges. "
            "It helps inspect transitions and image structure."
        )

    with st.expander("Copy-Move Detection"):
        st.write(
            "Uses feature matching to identify similar image areas "
            "that could be candidates for copy-move manipulation. "
            "Repeated natural patterns can cause false positives."
        )

    with st.expander("Typography Analysis"):
        st.write(
            "Uses preliminary image-processing heuristics to inspect "
            "text-like components, spacing, alignment and edge "
            "characteristics. It does not reliably identify exact fonts "
            "or prove that text has been edited."
        )

    with st.expander("Review Priority Score"):
        st.write(
            "Combines selected forensic findings into an experimental "
            "review-priority score. It is not a calibrated probability "
            "of image manipulation."
        )

    with st.expander("Structural Similarity and Pixel Differences"):
        st.write(
            "Structural similarity measures how visually similar "
            "two images are. Pixel differences highlight areas where "
            "the images differ. Neither method determines which image "
            "is authentic."
        )

    with st.expander("OCR Comparison"):
        st.write(
            "Extracts text from both images and identifies possible "
            "added, removed or modified text. OCR can misread small, "
            "blurred or unusual characters."
        )

    st.markdown("---")
    st.subheader("Important Limitations")

    st.warning("""
    VerifEye is an experimental AI-assisted digital image
    forensics prototype.

    - No individual indicator proves image manipulation.
    - ELA is intended for JPEG analysis.
    - Repeated natural patterns may affect copy-move detection.
    - OCR can produce incorrect text.
    - Typography checks are heuristic estimates.
    - The review-priority score is not a probability.
    - A comparison cannot establish which image is original.

    Always review the original evidence and use independent
    information before drawing conclusions.
    """)

    st.markdown("---")

    st.caption(
        "VerifEye | AI-Assisted Digital Image Forensics"
    )
