from __future__ import annotations
from typing import TypedDict, Any
from openai import OpenAI
from langgraph.graph import StateGraph, END
from config import OPENAI_MODEL
from knowledge_loader import load, build_context_block
from schemas import LaunchPlan
from tools.guardrails import check_guardrails

_client = OpenAI()


def _feedback_block(feedback: str | None) -> str:
    if not feedback:
        return ""
    return f"\n\n⚠️ OWNER FEEDBACK — apply this precisely before anything else:\n{feedback}\n"


class LaunchState(TypedDict):
    user_input: str
    feedback: str | None
    launch_output: dict[str, Any] | None
    guardrails_output: dict[str, Any] | None


def plan_launch(state: LaunchState) -> LaunchState:
    knowledge = load("business_strategy.md", "content_strategy.md", "brand_identity.md")
    context = build_context_block(state["user_input"])
    system = f"""You are SAMA's launch planning expert. Create a day-by-day launch timeline from T-21 to T+7.
{_feedback_block(state.get('feedback'))}
{knowledge}
{context}

Scale the timeline to the collection size. Assign specific content items to each day.
Phases: Pre-launch → Teaser → Preview → Launch → Post-launch

Respond with JSON only:
{{
  "collection_name": "...",
  "timeline": [
    {{"day_offset": -21, "date_label": "T-21", "phase": "Pre-launch", "content_item": "...", "platform": "...", "notes": "..."}}
  ]
}}"""

    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": state["user_input"]},
        ],
        response_format={"type": "json_object"},
    )
    result = LaunchPlan.model_validate_json(resp.choices[0].message.content)
    return {**state, "launch_output": result.model_dump()}


def guardrails_node(state: LaunchState) -> LaunchState:
    result = check_guardrails(str(state["launch_output"]))
    return {**state, "guardrails_output": result.model_dump()}


def build_graph() -> Any:
    g = StateGraph(LaunchState)
    g.add_node("run_plan", plan_launch)
    g.add_node("run_guardrails", guardrails_node)
    g.set_entry_point("run_plan")
    g.add_edge("run_plan", "run_guardrails")
    g.add_edge("run_guardrails", END)
    return g.compile()


graph = build_graph()


def run(user_input: str, feedback: str | None = None) -> dict:
    result = graph.invoke({"user_input": user_input, "feedback": feedback, "launch_output": None, "guardrails_output": None})
    return {"plan": result["launch_output"], "guardrails": result["guardrails_output"]}
