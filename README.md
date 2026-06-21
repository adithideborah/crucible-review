# The Crucible Review

> **Ideas strengthened through structured challenge.**

The Crucible Review is an AI-powered adversarial thinking partner designed to help users improve the quality of their reasoning before taking action.

Rather than providing a single answer, The Crucible Review evaluates ideas through a structured multi-agent review process that clarifies assumptions, challenges weak reasoning, evaluates methodology, and synthesizes actionable recommendations.

The goal is not to replace human judgment, but to sharpen it.

---

## Why This Exists

Modern AI tools are excellent at generating answers.

However, many users accept those answers without deeply engaging with the underlying reasoning.

The Crucible Review takes a different approach.

Instead of acting as an answer engine, it acts as a structured thinking partner that helps users:

* Clarify vague ideas
* Surface hidden assumptions
* Identify risks and blind spots
* Evaluate methodological rigor
* Develop stronger conclusions

Whether you're evaluating a research proposal, startup concept, product strategy, career decision, or operational problem, The Crucible Review helps strengthen ideas through deliberate challenge.

---

## How It Works

The Crucible Review uses a four-agent architecture.

### 🔦 Clarifier

Refines the problem statement, identifies ambiguities, and ensures the idea is clearly defined before evaluation begins.

### 🚩 Skeptic

Challenges assumptions, identifies risks, highlights blind spots, and explores potential failure modes.

### 📐 Methodologist

Evaluates whether the proposed approach is logically sound, evidence-based, and methodologically rigorous.

### 🧩 Synthesizer

Combines insights from the previous agents into a structured final review with actionable recommendations.

---

## Example Use Cases

* Research proposal evaluation
* Startup idea validation
* Product strategy review
* Business process improvement
* Career decision analysis
* Policy and operational planning
* Personal decision-making frameworks

---

## Features

* Multi-agent adversarial reasoning workflow
* Structured review reports
* Assumption and risk analysis
* Methodology evaluation
* Actionable recommendations
* Downloadable PDF reports
* Streamlit-based interface

---

## Technology Stack

* Python
* Streamlit
* Anthropic Claude
* ReportLab
* python-dotenv

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/crucible-review.git
cd crucible-review
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

---

## Environment Variables

Required:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Never commit your `.env` file or API keys to source control.

---

## Project Structure

```text
crucible-review/
│
├── app.py
├── agents.py
├── prompts.py
├── pdf_generator.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

---

## Future Roadmap

* Enhanced PDF reports and visual summaries
* Research-specific review templates
* Scoring and confidence framework
* Additional reviewer personas
* Multi-model evaluation support
* Streamlit Cloud deployment

---

## Author

**Dr. Adithi Deborah Chakravarthy**

Ph.D. Information Technology

Applied AI | Machine Learning | Human-Centered AI

---

## License

This project is provided for educational and portfolio purposes.
