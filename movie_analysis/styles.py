from __future__ import annotations

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg-top: #07111f;
    --bg-mid: #10233a;
    --bg-bottom: #040914;
    --surface: rgba(8, 20, 36, 0.76);
    --surface-strong: rgba(14, 31, 54, 0.92);
    --surface-soft: rgba(255, 255, 255, 0.06);
    --border: rgba(255, 255, 255, 0.08);
    --text-main: #f5f7fb;
    --text-muted: #b1c4d8;
    --accent: #ff8a3d;
    --accent-soft: #ffd166;
    --accent-cool: #12c6c2;
}

html, body, [class*="css"], .stApp {
    font-family: "Manrope", "Aptos", "Segoe UI", sans-serif;
}

.stApp {
    color: var(--text-main);
    background:
        radial-gradient(circle at top left, rgba(255, 138, 61, 0.18), transparent 26%),
        radial-gradient(circle at top right, rgba(18, 198, 194, 0.15), transparent 24%),
        linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 48%, var(--bg-bottom) 100%);
}

.block-container {
    max-width: 1380px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(6, 17, 31, 0.96) 0%, rgba(10, 25, 45, 0.98) 100%);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .st-emotion-cache-16txtl3,
section[data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
    padding-top: 1.75rem;
}

.hero-card {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border);
    background:
        linear-gradient(135deg, rgba(255, 138, 61, 0.18), rgba(18, 198, 194, 0.1)),
        rgba(7, 19, 35, 0.9);
    border-radius: 28px;
    padding: 2rem 2.2rem;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
    margin-bottom: 1.25rem;
}

.hero-card::after {
    content: "";
    position: absolute;
    right: -60px;
    top: -60px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, rgba(255, 209, 102, 0.35), transparent 65%);
}

.eyebrow {
    display: inline-flex;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    color: var(--accent-soft);
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.85rem;
}

.hero-title {
    font-size: 2.35rem;
    line-height: 1.05;
    margin: 0;
    max-width: 760px;
}

.hero-description {
    max-width: 760px;
    color: var(--text-muted);
    font-size: 1.02rem;
    margin-top: 0.9rem;
}

.hero-meta {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 1.2rem;
}

.hero-chip {
    padding: 0.55rem 0.9rem;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: var(--text-main);
}

.metric-card {
    border: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(12, 29, 49, 0.94) 0%, rgba(7, 20, 35, 0.9) 100%);
    border-radius: 24px;
    padding: 1.2rem 1.3rem;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.22);
    min-height: 152px;
}

.metric-label {
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.8rem;
    margin-bottom: 0.7rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.5rem;
}

.metric-detail {
    color: var(--text-muted);
    font-size: 0.95rem;
}

.section-card {
    border: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(8, 21, 37, 0.88) 0%, rgba(7, 16, 29, 0.92) 100%);
    border-radius: 24px;
    padding: 1.25rem 1.3rem 1rem 1.3rem;
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.12rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.section-caption {
    color: var(--text-muted);
    font-size: 0.94rem;
}

.insight-card {
    border: 1px solid rgba(255, 255, 255, 0.06);
    background: rgba(255, 255, 255, 0.04);
    border-radius: 18px;
    padding: 1rem 1.05rem;
    margin-top: 0.85rem;
}

.insight-title {
    color: var(--accent-soft);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.78rem;
    margin-bottom: 0.4rem;
}

.insight-body {
    color: var(--text-main);
    font-size: 0.97rem;
    line-height: 1.55;
}

.small-note {
    color: var(--text-muted);
    font-size: 0.9rem;
}

[data-testid="stMetric"] {
    border-radius: 18px;
    border: 1px solid var(--border);
    padding: 1rem;
    background: var(--surface-soft);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.65rem;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    padding: 0 1rem;
    border-radius: 999px;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid transparent;
}

.stTabs [aria-selected="true"] {
    color: var(--text-main);
    background: linear-gradient(135deg, rgba(255, 138, 61, 0.22), rgba(18, 198, 194, 0.16));
    border-color: rgba(255, 255, 255, 0.08);
}

div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid var(--border);
}

div[data-testid="stAlert"] {
    border-radius: 18px;
}
</style>
"""


def hero_card(source_label: str, row_count: int, genre_count: int) -> str:
    return f"""
    <div class="hero-card">
        <div class="eyebrow">Movie Analysis Studio</div>
        <h1 class="hero-title">Movie analysis dashboard for cleaning, insights, and prediction</h1>
        <p class="hero-description">
            This app covers all required tasks in the assignment: missing-data cleaning, genre popularity,
            rating versus revenue analysis, top movie visualization, and prediction for rating or revenue.
        </p>
        <div class="hero-meta">
            <div class="hero-chip"><strong>Source:</strong> {source_label}</div>
            <div class="hero-chip"><strong>Rows:</strong> {row_count}</div>
            <div class="hero-chip"><strong>Genres:</strong> {genre_count}</div>
        </div>
    </div>
    """


def metric_card(title: str, value: str, detail: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-detail">{detail}</div>
    </div>
    """


def section_header(title: str, caption: str) -> str:
    return f"""
    <div class="section-card">
        <div class="section-title">{title}</div>
        <div class="section-caption">{caption}</div>
    </div>
    """


def insight_card(title: str, body: str) -> str:
    return f"""
    <div class="insight-card">
        <div class="insight-title">{title}</div>
        <div class="insight-body">{body}</div>
    </div>
    """
