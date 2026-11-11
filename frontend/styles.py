def load_styles():
    return """
    <style>
    .stApp {
        background: #0b1220;
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background: #111c2e;
    }

    .hero {
        padding: 28px;
        border: 1px solid #263b59;
        border-radius: 18px;
        background: linear-gradient(120deg, #14243b, #101a2b);
        margin-bottom: 24px;
    }

    .hero h1 {
        color: #f8fafc;
        font-size: 38px;
        margin-bottom: 5px;
    }

    .hero p {
        color: #a9bdd7;
        font-size: 15px;
    }

    .metric-card {
        background: #142238;
        border: 1px solid #2a4262;
        padding: 18px;
        border-radius: 14px;
        min-height: 110px;
    }

    .metric-label {
        color: #9fb4ce;
        font-size: 13px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 25px;
        font-weight: 700;
        margin-top: 8px;
    }

    .finding-card {
        background: #142238;
        border: 1px solid #2a4262;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
    }

    .muted {
        color: #9fb4ce;
    }

    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 9px;
        padding: 9px 18px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        color: white;
        border: none;
    }

    </style>
    """