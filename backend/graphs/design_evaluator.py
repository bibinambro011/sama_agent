from __future__ import annotations
from typing import TypedDict, Any
from openai import OpenAI
from langgraph.graph import StateGraph, END
from config import OPENAI_MODEL
from knowledge_loader import load
from schemas import DesignEvaluation
from tools.guardrails import check_guardrails

_client = OpenAI()


def _feedback_block(feedback: str | None) -> str:
    if not feedback:
        return ""
    return f"\n\n⚠️ OWNER FEEDBACK — apply this precisely before anything else:\n{feedback}\n"


class EvaluatorState(TypedDict):
    user_input: str
    image_b64: str | None
    feedback: str | None
    eval_output: dict[str, Any] | None
    guardrails_output: dict[str, Any] | None


def evaluate_design(state: EvaluatorState) -> EvaluatorState:
    knowledge = load("brand_identity.md", "evaluation_system.md", "customer_psychology.md")
    system = f"""You are SAMA's design evaluation expert. Evaluate honestly and constructively.
{_feedback_block(state.get('feedback'))}
{knowledge}

Never answer with just "beautiful". Always return what works, what doesn't, what to change.

Respond with JSON only:
{{
  "scores": {{
    "visual_appeal": 1-10, "sama_brand_fit": 1-10, "wearability": 1-10, "comfort": 1-10,
    "uniqueness": 1-10, "customer_appeal": 1-10, "production_feasibility": 1-10,
    "cost_feasibility": 1-10, "styling_potential": 1-10, "instagram_potential": 1-10,
    "repeat_sale_potential": 1-10
  }},
  "overall_score": 0.0,
  "what_works": ["..."], "what_doesnt": ["..."], "what_to_change": ["..."],
  "how_to_make_more_sama": ["..."], "how_to_make_more_commercial": ["..."],
  "retain": ["..."], "modify": ["..."], "sleeve_options": ["..."],
  "neckline_options": ["..."], "back_options": ["..."],
  "fabric_suggestions": ["..."], "embellishment_suggestions": ["..."]
}}"""

    user_content: list[dict] = [{"type": "text", "text": state["user_input"] or "Evaluate this design."}]
    if state.get("image_b64"):
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{state['image_b64']}"},
        })

    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
    )
    result = DesignEvaluation.model_validate_json(resp.choices[0].message.content)
    return {**state, "eval_output": result.model_dump()}


def guardrails_node(state: EvaluatorState) -> EvaluatorState:
    result = check_guardrails(str(state["eval_output"]))
    return {**state, "guardrails_output": result.model_dump()}


def build_graph() -> Any:
    g = StateGraph(EvaluatorState)
    g.add_node("run_evaluate", evaluate_design)
    g.add_node("run_guardrails", guardrails_node)
    g.set_entry_point("run_evaluate")
    g.add_edge("run_evaluate", "run_guardrails")
    g.add_edge("run_guardrails", END)
    return g.compile()


graph = build_graph()


def run(user_input: str, image_b64: str | None = None, feedback: str | None = None) -> dict:
    result = graph.invoke({"user_input": user_input, "image_b64": image_b64, "feedback": feedback, "eval_output": None, "guardrails_output": None})
    return {"evaluation": result["eval_output"], "guardrails": result["guardrails_output"]}
