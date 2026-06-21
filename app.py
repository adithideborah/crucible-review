from pdf_generator import build_pdf
import json
import streamlit as st

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


# -----------------------------
# Session state
# -----------------------------

if "brief" not in st.session_state:
    st.session_state.brief = None

if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None

if "clarifier_output" not in st.session_state:
    st.session_state.clarifier_output = None

if "skeptic_output" not in st.session_state:
    st.session_state.skeptic_output = None

if "methodologist_output" not in st.session_state:
    st.session_state.methodologist_output = None


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="The Crucible Review",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ The Crucible Review")

st.subheader(
    "Your adversarial thinking partner."
)

st.caption(
    "Clarify assumptions. Challenge conclusions. Design better investigations."
)

st.caption(
    "The Crucible Review structures inquiry. It does not replace expert, legal, clinical, financial, or professional judgment."
)


# -----------------------------
# Input
# -----------------------------

idea = st.text_area(
    "Describe an idea, challenge, decision, or problem you'd like to investigate:",
    placeholder="Example: A state agency invested in a new case management system, but processing times and employee satisfaction worsened.",
    height=150
)

generate_button = st.button("Generate Crucible Brief")


# -----------------------------
# Run agents
# -----------------------------

if generate_button:
    if not idea.strip():
        st.warning("Please enter an idea first.")
    else:
        with st.spinner("The Clarifier is refining your idea..."):
            clarifier_output = run_clarifier_agent(idea)

        with st.spinner("The Skeptic is stress-testing your idea..."):
            skeptic_output = run_skeptic_agent(
                idea,
                clarifier_output
            )

        with st.spinner("The Methodologist is designing a validation plan..."):
            methodologist_output = run_methodologist_agent(
                idea,
                clarifier_output,
                skeptic_output
            )

        with st.spinner("The Synthesizer is creating your Crucible Brief..."):
            final_brief = run_synthesizer_agent(
                idea,
                clarifier_output,
                skeptic_output,
                methodologist_output
            )

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


# -----------------------------
# Render output
# -----------------------------

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
    "Other": "📌"
    }


    severity_colors = {
        "High": "#ffe0e0",
        "Medium": "#fff1cc",
        "Low": "#e4f8e4"
    }

    severity_icons = {
        "High": "🟥",
        "Medium": "🟧",
        "Low": "🟨"
    }

    st.markdown("---")
    st.markdown("## 📌 Crucible Brief")

    st.markdown("### 📄 Executive Summary")

    st.markdown(
        f"""
        <div style="
            padding:16px;   
            border-radius:14px;
            background-color:#f5f7ff;
            border-left:6px solid #4a6cf7;
            margin-bottom:20px;
        ">
        <b>{brief.get('executive_summary','')}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    domain = brief.get("domain","Other")
    icon = domain_icons.get(domain,"📌")

    st.markdown(
        f"### {icon} {domain}"
    )

    st.info(brief.get("idea_under_test", ""))

    st.success(
        f"**Working Hypothesis:** {brief.get('hypothesis', '')}"
    )

    st.markdown("### 🧭 Assumption Map")

    for item in brief.get("assumptions", []):
        st.markdown(
            f"""
            <div style="
                padding: 14px;
                border-radius: 14px;
                background-color: #f7f7f7;
                margin-bottom: 12px;
                border-left: 6px solid #666;
            ">
                <b>{item.get("title", "")}</b><br>
                <span style="color:#555;">Why: {item.get("why", "")}</span><br>
                <span style="color:#333;">Test: {item.get("test", "")}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 🚦 Risk Radar")

    for risk in brief.get("risks", []):
        severity = risk.get("severity", "Medium")
        color = severity_colors.get(severity, "#eeeeee")
        icon = severity_icons.get(severity, "⚠️")

        st.markdown(
            f"""
            <div style="
                padding: 14px;
                border-radius: 14px;
                background-color: {color};
                margin-bottom: 12px;
            ">
                <b>{icon} {severity} Risk: {risk.get("title", "")}</b><br>
                <span>{risk.get("why", "")}</span>
            </div>
            """,
            unsafe_allow_html=True
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

    for i, question in enumerate(
    brief.get("mentor_questions", []),
    start=1
    ):
        st.markdown(
            f"""
            <div style="
                padding:14px;
                border-radius:12px;
                background:#fff8e6;
                border-left:5px solid #e0b000;
                margin-bottom:10px;
            ">
                <b>Challenge #{i}</b><br><br>
                {question}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.download_button(
        label="📄 Download PDF",
        data=st.session_state.pdf_data,
        file_name="crucible_brief.pdf",
        mime="application/pdf"
    )

    st.markdown("---")

    st.markdown("### Behind the Analysis")

    with st.expander("🔍 Clarifier"):
        st.markdown(st.session_state.clarifier_output)

    with st.expander("🚩 Skeptic"):
        st.markdown(st.session_state.skeptic_output)

    with st.expander("🧪 Methodologist"):
        st.markdown(st.session_state.methodologist_output)