from pdf_generator import build_pdf
import json
import html
import textwrap
import streamlit as st
import streamlit.components.v1 as components

from agents import (
    run_clarifier_agent,
    run_skeptic_agent,
    run_methodologist_agent,
    run_synthesizer_agent,
)


def extract_json(text: str):
    decoder = json.JSONDecoder()
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found.")

    obj, _ = decoder.raw_decode(text[start:])
    return obj


def safe_text(value, fallback=""):
    if value is None:
        value = fallback
    return html.escape(str(value))


def render_html(html_content: str):
    """Render generated HTML without Markdown interpreting indentation as code."""
    cleaned_html = textwrap.dedent(html_content).strip()
    st.markdown(cleaned_html, unsafe_allow_html=True)


def count_words(value):
    return len(str(value or "").split())


def calculate_crucible_scores(brief):
    risks = brief.get("risks", []) or []
    evidence = brief.get("evidence_needed", []) or []
    minimum_test = brief.get("minimum_test", {}) or {}
    hypothesis_words = count_words(brief.get("hypothesis"))
    idea_words = count_words(brief.get("idea_under_test"))
    summary_words = count_words(brief.get("executive_summary"))
    clarity = min(100, 35 + min(25, hypothesis_words * 2) + min(20, idea_words) + min(20, summary_words // 2))
    evidence_specificity = sum(1 for item in evidence if count_words(item) >= 5)
    evidence_score = min(100, 25 + len(evidence) * 10 + evidence_specificity * 8)
    high_or_medium_risks = sum(1 for risk in risks if risk.get("severity", "Medium") in ["High", "Medium"])
    risk_awareness = min(100, 35 + len(risks) * 10 + high_or_medium_risks * 8)
    test_fields = ["sample", "method", "output", "decision"]
    completed_test_fields = sum(1 for field in test_fields if count_words(minimum_test.get(field)) >= 3)
    testability = min(100, 30 + completed_test_fields * 17 + len(evidence) * 3)
    decision_readiness = round((clarity * 0.25) + (evidence_score * 0.20) + (risk_awareness * 0.20) + (testability * 0.35))
    overall = round((clarity + evidence_score + risk_awareness + testability + decision_readiness) / 5)
    return {"overall": overall, "clarity": round(clarity), "evidence": round(evidence_score), "risk_awareness": round(risk_awareness), "testability": round(testability), "decision_readiness": round(decision_readiness)}


def score_label(score):
    if score >= 80:
        return "Strong Foundation"
    if score >= 65:
        return "Promising, Needs Proof"
    if score >= 50:
        return "Early, Validate First"
    return "Premature"


def readiness_badge(score):
    if score >= 80:
        return "🟢 Ready for Pilot"
    if score >= 65:
        return "🟡 Needs Evidence"
    if score >= 50:
        return "🟠 Significant Unknowns"
    return "🔴 Premature"


def primary_risk_label(brief):
    risks = brief.get("risks", []) or []
    if not risks:
        return "Not Identified"
    severity_rank = {"High": 3, "Medium": 2, "Low": 1}
    top_risk = sorted(risks, key=lambda risk: severity_rank.get(risk.get("severity", "Medium"), 2), reverse=True)[0]
    return top_risk.get("title", "Review Required")


def progress_bar_html(label, score):
    return f"""
    <div class="score-row">
        <div class="score-row-top"><span>{safe_text(label)}</span><strong>{score}</strong></div>
        <div class="score-track"><div class="score-fill" style="width:{max(0, min(100, score))}%;"></div></div>
    </div>
    """


def render_executive_dashboard(brief, domain_icons):
    domain = brief.get("domain", "Other")
    icon = domain_icons.get(domain, "📌")
    scores = calculate_crucible_scores(brief)
    primary_risk = primary_risk_label(brief)
    score_rows = "".join([
        progress_bar_html("Clarity", scores["clarity"]),
        progress_bar_html("Evidence", scores["evidence"]),
        progress_bar_html("Risk Awareness", scores["risk_awareness"]),
        progress_bar_html("Testability", scores["testability"]),
        progress_bar_html("Decision Readiness", scores["decision_readiness"]),
    ])
    html_block = f"""
    <div class="report-shell">
        <div class="report-kicker">EXECUTIVE REVIEW</div>
        <div class="report-title-row">
            <div>
                <div class="report-title">🔥 The Crucible Review</div>
                <div class="report-subtitle">Structured challenge brief · Generated just now</div>
            </div>
            <div class="score-pill"><span>Crucible Score</span><strong>{scores["overall"]}</strong><em>{safe_text(score_label(scores["overall"]))}</em></div>
        </div>
        <div class="executive-card"><div class="section-eyebrow">Executive Assessment</div><p>{safe_text(brief.get("executive_summary", ""))}</p></div>
        <div class="metric-grid">
            <div class="metric-card"><span>Domain</span><strong>{icon} {safe_text(domain)}</strong></div>
            <div class="metric-card"><span>Decision Readiness</span><strong>{safe_text(readiness_badge(scores["decision_readiness"]))}</strong></div>
            <div class="metric-card"><span>Primary Risk</span><strong>{safe_text(primary_risk)}</strong></div>
            <div class="metric-card"><span>Evidence Posture</span><strong>{safe_text(score_label(scores["evidence"]))}</strong></div>
        </div>
        <div class="dashboard-grid">
            <div class="hypothesis-card"><div class="section-eyebrow">Idea Under Test</div><p>{safe_text(brief.get("idea_under_test", ""))}</p><div class="hypothesis-divider"></div><div class="section-eyebrow">Working Hypothesis</div><p>{safe_text(brief.get("hypothesis", ""))}</p></div>
            <div class="score-card"><div class="section-eyebrow">Score Breakdown</div>{score_rows}</div>
        </div>
    </div>
    """
    st.markdown(html_block, unsafe_allow_html=True)


st.set_page_config(
    page_title="The Crucible Review",
    page_icon="🔥",
    layout="wide",
)


for key in [
    "brief",
    "pdf_data",
    "clarifier_output",
    "skeptic_output",
    "methodologist_output",
]:
    if key not in st.session_state:
        st.session_state[key] = None


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: #ffffff;
}

.block-container {
    padding-top: 1.5rem;
    max-width: 1220px;
}

label {
    color: #071C3A !important;
    font-weight: 700 !important;
    font-size: 16px !important;
}

textarea {
    border-radius: 14px !important;
    border: 1px solid #D1D5DB !important;
    font-size: 16px !important;
}

textarea:focus {
    border-color: #082B63 !important;
    box-shadow: 0 0 0 1px #082B63 !important;
}

.stButton > button,
.stDownloadButton > button {
    background: #082B63;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1.4rem;
    font-weight: 700;
    font-size: 16px;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #061F49;
    color: white;
    border: none;
}

.result-card {
    padding: 18px;
    border-radius: 14px;
    background: #F8FAFC;
    border-left: 6px solid #082B63;
    margin-bottom: 18px;
}

.assumption-card {
    padding: 15px;
    border-radius: 14px;
    background-color: #F8FAFC;
    margin-bottom: 12px;
    border-left: 5px solid #082B63;
}

.challenge-card {
    padding: 15px;
    border-radius: 14px;
    background: #FFF7ED;
    border-left: 5px solid #F97316;
    margin-bottom: 12px;
}


.report-shell { border: 1px solid #E5E7EB; border-radius: 22px; padding: 34px; background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%); box-shadow: 0 18px 45px rgba(8, 43, 99, 0.07); margin: 24px 0 22px 0; }
.report-kicker, .section-eyebrow { color: #082B63; font-size: 12px; font-weight: 800; letter-spacing: 0.11em; text-transform: uppercase; }
.report-title-row { display: flex; justify-content: space-between; gap: 24px; align-items: flex-start; margin-top: 10px; }
.report-title { color: #071C3A; font-size: 38px; line-height: 1.05; letter-spacing: -1.1px; font-weight: 850; }
.report-subtitle { color: #64748B; font-size: 15px; margin-top: 10px; }
.score-pill { min-width: 190px; border: 1px solid #DBEAFE; border-radius: 18px; background: #FFFFFF; padding: 18px 20px; text-align: center; }
.score-pill span, .metric-card span { display: block; color: #64748B; font-size: 12px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; }
.score-pill strong { display: block; color: #082B63; font-size: 48px; line-height: 1; margin-top: 7px; }
.score-pill em { display: block; color: #334155; font-size: 13px; font-style: normal; font-weight: 800; margin-top: 7px; }
.executive-card, .hypothesis-card, .score-card, .modern-section, .verdict-card { border: 1px solid #E5E7EB; border-radius: 18px; background: #FFFFFF; padding: 24px; }
.executive-card { margin-top: 26px; border-left: 6px solid #082B63; }
.executive-card p, .hypothesis-card p, .verdict-card p { color: #1F2937; font-size: 17px; line-height: 1.68; margin: 10px 0 0 0; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
.metric-card { border: 1px solid #E5E7EB; border-radius: 16px; background: #FFFFFF; padding: 18px; }
.metric-card strong { display: block; color: #071C3A; font-size: 17px; line-height: 1.25; margin-top: 8px; }
.dashboard-grid { display: grid; grid-template-columns: 1.35fr 0.85fr; gap: 18px; margin-top: 18px; }
.hypothesis-divider { border-top: 1px solid #E5E7EB; margin: 20px 0; }
.score-row { margin-top: 15px; }
.score-row-top { display: flex; justify-content: space-between; color: #334155; font-size: 14px; font-weight: 800; margin-bottom: 7px; }
.score-track { height: 9px; border-radius: 999px; background: #E5E7EB; overflow: hidden; }
.score-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #082B63, #F97316); }
.modern-section { margin-bottom: 18px; }
.modern-section-title { font-size: 26px; color: #071C3A; font-weight: 850; letter-spacing: -0.5px; margin: 30px 0 14px 0; }
.assumption-grid, .challenge-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.assumption-card, .challenge-card { padding: 18px; border-radius: 16px; background-color: #FFFFFF; margin-bottom: 0; border: 1px solid #E5E7EB; border-left: 5px solid #082B63; }
.challenge-card { background: #FFF7ED; border-left-color: #F97316; }
.card-number { color: #64748B; font-size: 12px; font-weight: 850; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px; }
.card-heading { color: #071C3A; font-weight: 850; font-size: 17px; margin-bottom: 10px; }
.card-body { color: #334155; font-size: 14.5px; line-height: 1.6; }
.risk-card { border-radius: 16px; padding: 18px; margin-bottom: 12px; border: 1px solid #E5E7EB; background: #FFFFFF; }
.risk-badge { display: inline-block; border-radius: 999px; padding: 5px 10px; font-size: 12px; font-weight: 850; margin-bottom: 10px; }
.badge-high { background: #FEE2E2; color: #991B1B; }
.badge-medium { background: #FEF3C7; color: #92400E; }
.badge-low { background: #DCFCE7; color: #166534; }
.evidence-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.evidence-item { padding: 14px; border: 1px solid #E5E7EB; border-radius: 14px; background: #F8FAFC; color: #1F2937; font-size: 14.5px; line-height: 1.5; }
.investigation-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.protocol-card { padding: 16px; border-radius: 14px; background: #F8FAFC; border: 1px solid #E5E7EB; }
.protocol-card strong { display: block; color: #082B63; font-size: 13px; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }
.protocol-card span { color: #1F2937; font-size: 14.5px; line-height: 1.5; }
.verdict-card { border-left: 6px solid #F97316; margin: 24px 0; }
@media (max-width: 900px) { .report-title-row, .dashboard-grid { grid-template-columns: 1fr; display: grid; } .metric-grid, .assumption-grid, .challenge-grid, .evidence-list, .investigation-grid { grid-template-columns: 1fr; } }

</style>
""", unsafe_allow_html=True)


components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #ffffff;
    color: #071C3A;
}

.hero {
    border: 1px solid #E5E7EB;
    border-left: 8px solid #082B63;
    border-radius: 18px;
    padding: 52px 56px 38px 56px;
    background: #ffffff;
}

.title-row {
    display: flex;
    align-items: center;
    gap: 20px;
}

.flame-icon {
    width: 64px;
    height: 64px;
    flex-shrink: 0;
}

.title {
    font-size: 54px;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -1.7px;
    color: #071C3A;
}

.subtitle {
    margin-top: 30px;
    font-size: 22px;
    color: #082B63;
    font-weight: 750;
}

.description {
    margin-top: 12px;
    margin-bottom: 28px;
    font-size: 17px;
    color: #4B5563;
}

.notice {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: #F5F7FA;
    color: #1F2937;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 14px;
    line-height: 1.5;
}

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    margin-top: 32px;
}

.card {
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 32px 20px;
    text-align: center;
    background: #ffffff;
    transition: all 0.18s ease;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 32px rgba(8, 43, 99, 0.08);
    border-color: #BFDBFE;
}

.icon {
    width: 50px;
    height: 50px;
    margin-bottom: 16px;
    stroke: #082B63;
    stroke-width: 2.25;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.card-title {
    font-size: 20px;
    font-weight: 750;
    color: #071C3A;
    margin-bottom: 12px;
}

.card-text {
    font-size: 15px;
    line-height: 1.55;
    color: #4B5563;
}
</style>
</head>

<body>
    <div class="hero">
        <div class="title-row">
            <svg class="flame-icon" viewBox="0 0 64 64" fill="none">
                <path d="M32 58C20.5 58 12 49.6 12 38.8C12 29.8 17.8 23.1 23.4 17.1C27.2 13 30.7 9.2 31.6 4C40.5 10.5 44 18.2 42.8 26.8C46.2 24.8 48.5 21.4 49.4 17.5C56.2 25.5 59 32.1 59 39.6C59 50.2 50.3 58 32 58Z"
                      stroke="#082B63" stroke-width="3.5" stroke-linejoin="round"/>
                <path d="M32 55C24.8 55 19.8 50.1 19.8 43.8C19.8 38.1 23.4 34 27.3 30C30 27.2 32.4 24.8 32.8 21.5C38.6 26.3 40.4 31.4 39.1 37.2C41.5 36.2 43.2 34.2 44 31.7C48.3 36.6 49.8 40.4 49.8 44.2C49.8 50.5 44.3 55 32 55Z"
                      fill="#F97316"/>
            </svg>

            <div class="title">The Crucible Review</div>
        </div>

        <div class="subtitle">Ideas strengthened through structured challenge.</div>
        <div class="description">Clarify assumptions. Challenge conclusions. Design better investigations.</div>

        <div class="notice">
            🛡️ This is a thinking partner, not a replacement for expert, legal, clinical, financial, or professional judgment.
        </div>
    </div>

    <div class="cards">
        <div class="card">
            <svg class="icon" viewBox="0 0 24 24">
                <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/>
                <path d="M8 10h.01M12 10h.01M16 10h.01"/>
            </svg>
            <div class="card-title">Clarifier</div>
            <div class="card-text">Refines the problem<br>and exposes ambiguity.</div>
        </div>

        <div class="card">
            <svg class="icon" viewBox="0 0 24 24">
                <path d="M12 3v18"/>
                <path d="M5 21h14"/>
                <path d="M3 7h18"/>
                <path d="M6 7l-3 7h6l-3-7z"/>
                <path d="M18 7l-3 7h6l-3-7z"/>
            </svg>
            <div class="card-title">Skeptic</div>
            <div class="card-text">Challenges assumptions<br>and identifies risks.</div>
        </div>

        <div class="card">
            <svg class="icon" viewBox="0 0 24 24">
                <path d="M10 2v6L4.5 19A2 2 0 0 0 6.4 22h11.2a2 2 0 0 0 1.9-3L14 8V2"/>
                <path d="M8 2h8"/>
                <path d="M7 16h10"/>
                <path d="M11 19h.01M14 19h.01"/>
            </svg>
            <div class="card-title">Methodologist</div>
            <div class="card-text">Designs rigorous ways<br>to test ideas.</div>
        </div>

        <div class="card">
            <svg class="icon" viewBox="0 0 24 24">
                <path d="M19.4 13.5c.4-.3.6-.8.6-1.3V10a2 2 0 0 0-2-2h-2V6a2 2 0 0 0-2-2h-2.2c-.5 0-1 .2-1.3.6"/>
                <path d="M8 4H6a2 2 0 0 0-2 2v2h2a2 2 0 1 1 0 4H4v2a2 2 0 0 0 2 2h2v2a2 2 0 0 0 2 2h2"/>
                <path d="M16 16h2a2 2 0 0 0 2-2v-2"/>
            </svg>
            <div class="card-title">Synthesizer</div>
            <div class="card-text">Produces a final<br>actionable review.</div>
        </div>
    </div>
</body>
</html>
""", height=580, scrolling=False)


idea = st.text_area(
    "Describe an idea, challenge, decision, or problem you'd like to investigate:",
    placeholder="Example: A state agency invested in a new case management system, but processing times and employee satisfaction worsened.",
    height=160,
)

generate_button = st.button("Generate Crucible Brief  →")


def render_progress_panel(status_box, active_step, completed_steps):
    steps = [
        ("Clarifier", "Refining the problem and exposing ambiguity."),
        ("Skeptic", "Challenging assumptions and identifying risks."),
        ("Methodologist", "Designing a practical validation plan."),
        ("Synthesizer", "Producing the final Crucible Brief."),
    ]

    rows = ""

    for idx, (name, description) in enumerate(steps):
        if idx in completed_steps:
            icon = "✓"
            icon_bg = "#DCFCE7"
            icon_color = "#166534"
            border = "#BBF7D0"
            status = "Complete"
        elif idx == active_step:
            icon = "●"
            icon_bg = "#DBEAFE"
            icon_color = "#082B63"
            border = "#BFDBFE"
            status = "In progress"
        else:
            icon = "○"
            icon_bg = "#F3F4F6"
            icon_color = "#6B7280"
            border = "#E5E7EB"
            status = "Waiting"

        rows += f"""
        <div class="step">
            <div class="step-icon" style="background:{icon_bg}; color:{icon_color}; border-color:{border};">
                {icon}
            </div>
            <div>
                <div class="step-title">
                    {name}
                    <span style="color:{icon_color};">{status}</span>
                </div>
                <div class="step-description">{description}</div>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    body {{
        margin: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: #ffffff;
    }}

    .panel {{
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 26px 28px;
        background: #ffffff;
    }}

    .panel-title {{
        font-size: 24px;
        font-weight: 800;
        color: #071C3A;
        margin-bottom: 8px;
    }}

    .panel-subtitle {{
        color: #4B5563;
        font-size: 15px;
        margin-bottom: 18px;
    }}

    .step {{
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 14px 0;
        border-top: 1px solid #F1F5F9;
    }}

    .step-icon {{
        width: 30px;
        height: 30px;
        border-radius: 999px;
        border: 1px solid;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        flex-shrink: 0;
    }}

    .step-title {{
        font-weight: 800;
        color: #071C3A;
        font-size: 16px;
    }}

    .step-title span {{
        font-size: 13px;
        font-weight: 700;
        margin-left: 8px;
    }}

    .step-description {{
        color: #4B5563;
        font-size: 14px;
        margin-top: 3px;
    }}
    </style>
    </head>

    <body>
        <div class="panel">
            <div class="panel-title">🔥 Running the Crucible</div>
            <div class="panel-subtitle">Your idea is moving through structured challenge.</div>
            {rows}
        </div>
    </body>
    </html>
    """

    status_box.empty()
    with status_box.container():
        components.html(html, height=365, scrolling=False)


if generate_button:
    if not idea.strip():
        st.warning("Please enter an idea first.")
    else:
        progress = st.progress(0)
        status_box = st.empty()

        render_progress_panel(status_box, active_step=0, completed_steps=[])
        progress.progress(5)

        clarifier_output = run_clarifier_agent(idea)

        render_progress_panel(status_box, active_step=1, completed_steps=[0])
        progress.progress(30)

        skeptic_output = run_skeptic_agent(idea, clarifier_output)

        render_progress_panel(status_box, active_step=2, completed_steps=[0, 1])
        progress.progress(55)

        methodologist_output = run_methodologist_agent(
            idea,
            clarifier_output,
            skeptic_output,
        )

        render_progress_panel(status_box, active_step=3, completed_steps=[0, 1, 2])
        progress.progress(80)

        final_brief = run_synthesizer_agent(
            idea,
            clarifier_output,
            skeptic_output,
            methodologist_output,
        )

        render_progress_panel(status_box, active_step=None, completed_steps=[0, 1, 2, 3])
        progress.progress(100)

        try:
            brief = extract_json(final_brief)
            pdf_data = build_pdf(brief)

            st.session_state.brief = brief
            st.session_state.pdf_data = pdf_data
            st.session_state.clarifier_output = clarifier_output
            st.session_state.skeptic_output = skeptic_output
            st.session_state.methodologist_output = methodologist_output

        except Exception as e:
            st.error("Could not parse Claude response as JSON.")
            st.code(final_brief)
            st.exception(e)
            st.stop()


if st.session_state.brief:
    brief = st.session_state.brief

    domain_icons = {
        "Research": "🔬",
        "Technical": "💻",
        "Business": "💰",
        "Operations": "🏢",
        "Policy": "🏛️",
        "Healthcare": "🏥",
        "Education": "🎓",
        "Personal": "👤",
        "Other": "📌",
    }

    severity_class = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}

    st.markdown("---")
    render_executive_dashboard(brief, domain_icons)

    st.download_button(label="📄 Download Full Report", data=st.session_state.pdf_data, file_name="crucible_brief.pdf", mime="application/pdf")

    assumption_cards = []
    for i, item in enumerate(brief.get("assumptions", []), start=1):
        assumption_cards.append(
            textwrap.dedent(
                f"""
                <div class="assumption-card">
                    <div class="card-number">Assumption {i}</div>
                    <div class="card-heading">{safe_text(item.get("title", ""))}</div>
                    <div class="card-body">
                        <strong>Why it matters:</strong> {safe_text(item.get("why", ""))}
                    </div>
                    <div class="card-body" style="margin-top:8px;">
                        <strong>How to test it:</strong> {safe_text(item.get("test", ""))}
                    </div>
                </div>
                """
            ).strip()
        )

    assumptions_html = "\n".join(assumption_cards)
    st.markdown(
        '<div class="modern-section-title">🧭 Assumption Map</div>',
        unsafe_allow_html=True,
    )
    render_html(
        f"""
        <div class="assumption-grid">
            {assumptions_html}
        </div>
        """
    )

    risk_cards = []
    for risk in brief.get("risks", []):
        severity = risk.get("severity", "Medium")
        badge_class = severity_class.get(severity, "badge-medium")
        risk_cards.append(
            textwrap.dedent(
                f"""
                <div class="risk-card">
                    <div class="risk-badge {badge_class}">{safe_text(severity)} Risk</div>
                    <div class="card-heading">{safe_text(risk.get("title", ""))}</div>
                    <div class="card-body">{safe_text(risk.get("why", ""))}</div>
                </div>
                """
            ).strip()
        )

    risks_html = "\n".join(risk_cards)
    st.markdown(
        '<div class="modern-section-title">🚦 Risk Radar</div>',
        unsafe_allow_html=True,
    )
    render_html(
        f"""
        <div class="modern-section">
            {risks_html}
        </div>
        """
    )

    evidence_items = [
        f'<div class="evidence-item">☐ {safe_text(evidence)}</div>'
        for evidence in brief.get("evidence_needed", [])
    ]
    evidence_html = "\n".join(evidence_items)
    st.markdown(
        '<div class="modern-section-title">🧾 Critical Evidence</div>',
        unsafe_allow_html=True,
    )
    render_html(
        f"""
        <div class="modern-section">
            <div class="evidence-list">
                {evidence_html}
            </div>
        </div>
        """
    )

    test = brief.get("minimum_test", {}) or {}
    protocol_items = [
        ("Sample", test.get("sample", "")),
        ("Method", test.get("method", "")),
        ("Output", test.get("output", "")),
        ("Decision", test.get("decision", "")),
    ]
    protocol_html = "\n".join(
        f"""
        <div class="protocol-card">
            <strong>{safe_text(label)}</strong>
            <span>{safe_text(value)}</span>
        </div>
        """.strip()
        for label, value in protocol_items
    )
    st.markdown(
        '<div class="modern-section-title">🧪 Minimum Viable Investigation</div>',
        unsafe_allow_html=True,
    )
    render_html(
        f"""
        <div class="modern-section">
            <div class="investigation-grid">
                {protocol_html}
            </div>
        </div>
        """
    )

    move_items = [
        f'<div class="evidence-item"><strong>{i}.</strong> {safe_text(move)}</div>'
        for i, move in enumerate(brief.get("next_moves", []), start=1)
    ]
    moves_html = "\n".join(move_items)
    st.markdown(
        '<div class="modern-section-title">🎯 Recommended Actions</div>',
        unsafe_allow_html=True,
    )
    render_html(
        f"""
        <div class="modern-section">
            <div class="evidence-list">
                {moves_html}
            </div>
        </div>
        """
    )

    challenge_cards = [
        textwrap.dedent(
            f"""
            <div class="challenge-card">
                <div class="card-number">Challenge {i}</div>
                <div class="card-body">{safe_text(question)}</div>
            </div>
            """
        ).strip()
        for i, question in enumerate(brief.get("mentor_questions", []), start=1)
    ]
    questions_html = "\n".join(challenge_cards)
    st.markdown(
        '<div class="modern-section-title">⚔️ Challenge Cards</div>',
        unsafe_allow_html=True,
    )
    render_html(
        f"""
        <div class="challenge-grid">
            {questions_html}
        </div>
        """
    )

    scores = calculate_crucible_scores(brief)

    recommendation = (
        brief.get("recommendation")
        or brief.get("verdict")
        or brief.get("final_recommendation")
    )

    verdict = recommendation or (
        f"{score_label(scores['overall'])}. "
        "Proceed by tightening the evidence base before making a "
        "high-confidence commitment. The next best step is a small, "
        "measurable test that can disconfirm the working hypothesis."
    )

    render_html(
        f"""
        <div class="verdict-card">
            <div class="section-eyebrow">The Crucible Verdict</div>
            <p>{safe_text(verdict)}</p>
        </div>
        """
    )

    st.markdown("---")
    st.markdown("### Behind the Analysis")
    with st.expander("🔦 Clarifier"):
        st.markdown(st.session_state.clarifier_output)
    with st.expander("🚩 Skeptic"):
        st.markdown(st.session_state.skeptic_output)
    with st.expander("📐 Methodologist"):
        st.markdown(st.session_state.methodologist_output)