from pdf_generator import build_pdf
import json
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

    severity_colors = {
        "High": "#FEE2E2",
        "Medium": "#FEF3C7",
        "Low": "#DCFCE7",
    }

    severity_icons = {
        "High": "🟥",
        "Medium": "🟧",
        "Low": "🟨",
    }

    st.markdown("---")
    st.markdown("## 📌 Crucible Brief")

    st.markdown("### 📄 Executive Summary")
    st.markdown(
        f"""
        <div class="result-card">
            <b>{brief.get('executive_summary', '')}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    domain = brief.get("domain", "Other")
    icon = domain_icons.get(domain, "📌")

    st.markdown(f"### {icon} {domain}")
    st.info(brief.get("idea_under_test", ""))

    st.success(f"**Working Hypothesis:** {brief.get('hypothesis', '')}")

    st.markdown("### 🧭 Assumption Map")

    for item in brief.get("assumptions", []):
        st.markdown(
            f"""
            <div class="assumption-card">
                <b>{item.get("title", "")}</b><br>
                <span style="color:#4B5563;">Why: {item.get("why", "")}</span><br>
                <span style="color:#1F2937;">Test: {item.get("test", "")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 🚦 Risk Radar")

    for risk in brief.get("risks", []):
        severity = risk.get("severity", "Medium")
        color = severity_colors.get(severity, "#F3F4F6")
        icon = severity_icons.get(severity, "⚠️")

        st.markdown(
            f"""
            <div style="
                padding: 15px;
                border-radius: 14px;
                background-color: {color};
                margin-bottom: 12px;
            ">
                <b>{icon} {severity} Risk: {risk.get("title", "")}</b><br>
                <span>{risk.get("why", "")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 🧾 Evidence Needed")

    evidence_items = brief.get("evidence_needed", [])
    cols = st.columns(2)

    for i, evidence in enumerate(evidence_items):
        with cols[i % 2]:
            st.markdown(f"✅ {evidence}")

    st.markdown("### 🧪 Minimum Viable Investigation")

    test = brief.get("minimum_test", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Sample**  \n{test.get('sample', '')}")
        st.markdown(f"**Output**  \n{test.get('output', '')}")

    with col2:
        st.markdown(f"**Method**  \n{test.get('method', '')}")
        st.markdown(f"**Decision**  \n{test.get('decision', '')}")

    st.markdown("### 🎯 Next 3 Moves")

    for i, move in enumerate(brief.get("next_moves", []), start=1):
        st.markdown(f"**{i}.** {move}")

    st.markdown("### ⚔️ Challenge Cards")

    for i, question in enumerate(brief.get("mentor_questions", []), start=1):
        st.markdown(
            f"""
            <div class="challenge-card">
                <b>Challenge #{i}</b><br><br>
                {question}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.download_button(
        label="📄 Download PDF",
        data=st.session_state.pdf_data,
        file_name="crucible_brief.pdf",
        mime="application/pdf",
    )

    st.markdown("---")
    st.markdown("### Behind the Analysis")

    with st.expander("🔦 Clarifier"):
        st.markdown(st.session_state.clarifier_output)

    with st.expander("🚩 Skeptic"):
        st.markdown(st.session_state.skeptic_output)

    with st.expander("📐 Methodologist"):
        st.markdown(st.session_state.methodologist_output)