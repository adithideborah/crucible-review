import os
from dotenv import load_dotenv
from anthropic import Anthropic

from prompts import CLARIFIER_PROMPT, SKEPTIC_PROMPT, METHODOLOGIST_PROMPT, SYNTHESIZER_PROMPT

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def run_clarifier_agent(user_idea: str) -> str:
    """
    Runs the Clarifier agent.
    Takes a vague research/project idea and returns a clearer research direction.
    """

    if not user_idea.strip():
        return "Please enter a research idea first."

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1100,
        system=CLARIFIER_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_idea
            }
        ]
    )

    return response.content[0].text


def run_skeptic_agent(user_idea: str, clarifier_output: str) -> str:
    """
    Runs the Skeptic agent.
    Challenges the clarified research direction.
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1100,
        system=SKEPTIC_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""
Original user idea:
{user_idea}

Clarifier Agent output:
{clarifier_output}

Now challenge this idea rigorously.
"""
            }
        ]
    )

    return response.content[0].text

def run_methodologist_agent(
    user_idea: str,
    clarifier_output: str,
    skeptic_output: str
) -> str:
    """
    Runs the Methodologist agent.
    Turns the clarified idea and skeptical critique into a validation plan.
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1100,
        system=METHODOLOGIST_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""
Original user idea:
{user_idea}

Clarifier Agent output:
{clarifier_output}

Skeptic Agent output:
{skeptic_output}

Now design a practical validation plan.
"""
            }
        ]
    )

    return response.content[0].text

def run_synthesizer_agent(
    user_idea: str,
    clarifier_output: str,
    skeptic_output: str,
    methodologist_output: str
) -> str:
    """
    Runs the Synthesizer agent.
    Combines all agent outputs into a polished Research Thinking Brief.
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYNTHESIZER_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""
Original user idea:
{user_idea}

Clarifier Agent output:
{clarifier_output}

Skeptic Agent output:
{skeptic_output}

Methodologist Agent output:
{methodologist_output}

Return only strict valid JSON that follows the schema exactly.
"""
            }
        ]
    )

    return response.content[0].text