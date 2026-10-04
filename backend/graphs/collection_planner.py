from __future__ import annotations
from typing import TypedDict, Any
from openai import OpenAI
from langgraph.graph import StateGraph, END
from config import OPENAI_MODEL
from knowledge_loader import load, build_context_block
from schemas import CollectionPlan
from tools.guardrails import check_guardrails
from memory.db import get_recent_style_memory

_client = OpenAI()


def _feedback_block(feedback: str | None) -> str:
    if not feedback:
        return ""
    return f"\n\n⚠️ OWNER FEEDBACK — apply this precisely before anything else:\n{feedback}\n"


class PlannerState(TypedDict):
    user_input: str
    feedback: str | None
    collection_output: dict[str, Any] | None
    guardrails_output: dict[str, Any] | None


def identify_and_generate(state: PlannerState) -> PlannerState:
    knowledge = load(
        "brand_identity.md", "collection_types.md", "layer_formats.md",
        "business_strategy.md", "customer_psychology.md",
    )
    context = build_context_block(state["user_input"])
    style_memory = get_recent_style_memory("collection", 3)
    memory_block = ""
    if style_memory:
        memory_block = "\n\nPrevious approved collections for style reference:\n" + "\n".join(
            f"- {s}" for s in style_memory
        )

    system = f"""You are SAMA's collection planning expert. Think like a talented boutique designer, Instagram strategist, merchandiser, and practical small-business consultant.
{_feedback_block(state.get('feedback'))}
{knowledge}
{context}{context}
{memory_block}

Generate a complete collection plan. If information is missing, make reasonable assumptions and list them clearly.

Respond with a JSON object matching this exact structure — no extra keys, no markdown:
{{
  "assumptions": ["..."],
  "collection_direction": {{
    "name_ideas": ["..."],
    "core_story": "...",
    "mood": "...",
    "colour_palette": ["..."],
    "fabric_direction": "...",
    "silhouette_direction": "...",
    "design_language": "...",
    "price_positioning": "...",
    "uniquely_sama": "...",
    "what_it_should_not_become": "..."
  }},
  "target_customer": "...",
  "design_ideas": [{{
    "garment_type": "...", "silhouette": "...", "neckline": "...", "sleeve": "...",
    "length": "...", "fabric": "...", "colour": "...", "special_detail": "...",
    "styling": "...", "occasion": "...", "why_customer_buys": "...",
    "production_complexity": "Low|Medium|High", "repeat_production_suitable": true
  }}],
  "fabric_and_colours": "...",
  "content_ideas": ["..."],
  "launch_strategy": "...",
  "business_strategy": "...",
  "immediate_actions": ["...", "...", "..."]
}}"""

    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": state["user_input"]},
        ],
        response_format={"type": "json_object"},
    )
    result = CollectionPlan.model_validate_json(resp.choices[0].message.content)
    return {**state, "collection_output": result.model_dump()}


def guardrails_node(state: PlannerState) -> PlannerState:
    result = check_guardrails(str(state["collection_output"]))
    return {**state, "guardrails_output": result.model_dump()}


def build_graph() -> Any:
    g = StateGraph(PlannerState)
    g.add_node("run_generate", identify_and_generate)
    g.add_node("run_guardrails", guardrails_node)
    g.set_entry_point("run_generate")
    g.add_edge("run_generate", "run_guardrails")
    g.add_edge("run_guardrails", END)
    return g.compile()


graph = build_graph()


def run(user_input: str, feedback: str | None = None) -> dict:
    result = graph.invoke({"user_input": user_input, "feedback": feedback, "collection_output": None, "guardrails_output": None})
    return {"plan": result["collection_output"], "guardrails": result["guardrails_output"]}
