from __future__ import annotations
from typing import TypedDict, Any
from openai import OpenAI
from langgraph.graph import StateGraph, END
from config import OPENAI_MODEL
from knowledge_loader import load
from schemas import ExpandedCollection
from tools.guardrails import check_guardrails

_client = OpenAI()


def _feedback_block(feedback: str | None) -> str:
    if not feedback:
        return ""
    return f"\n\n⚠️ OWNER FEEDBACK — apply this precisely before anything else:\n{feedback}\n"


class ExpanderState(TypedDict):
    user_input: str
    image_b64: str | None
    feedback: str | None
    expand_output: dict[str, Any] | None
    guardrails_output: dict[str, Any] | None


def expand_collection(state: ExpanderState) -> ExpanderState:
    knowledge = load("brand_identity.md", "layer_formats.md", "content_strategy.md", "business_strategy.md")
    system = f"""You are SAMA's collection expansion expert. Take one garment and expand it into a full mini collection.
{_feedback_block(state.get('feedback'))}
{knowledge}

Respond with JSON only. Every array item MUST be an object, never a plain string:
{{
  "base_garment": "...",
  "sleeve_variations": [
    {{"name": "...", "variation_type": "sleeve", "description": "...", "production_complexity": "Low", "repeat_production_suitable": true, "price_tier": "Entry"}},
    {{"name": "...", "variation_type": "sleeve", "description": "...", "production_complexity": "Medium", "repeat_production_suitable": true, "price_tier": "Mid"}},
    {{"name": "...", "variation_type": "sleeve", "description": "...", "production_complexity": "High", "repeat_production_suitable": false, "price_tier": "Premium"}}
  ],
  "neckline_variations": [
    {{"name": "...", "variation_type": "neckline", "description": "...", "production_complexity": "Low", "repeat_production_suitable": true, "price_tier": "Mid"}},
    {{"name": "...", "variation_type": "neckline", "description": "...", "production_complexity": "Medium", "repeat_production_suitable": true, "price_tier": "Mid"}}
  ],
  "colourways": [
    {{"name": "...", "variation_type": "colourway", "description": "...", "production_complexity": "Low", "repeat_production_suitable": true, "price_tier": "Entry"}},
    {{"name": "...", "variation_type": "colourway", "description": "...", "production_complexity": "Low", "repeat_production_suitable": true, "price_tier": "Mid"}},
    {{"name": "...", "variation_type": "colourway", "description": "...", "production_complexity": "Low", "repeat_production_suitable": true, "price_tier": "Mid"}}
  ],
  "bottoms": [
    {{"name": "...", "variation_type": "bottom", "description": "...", "production_complexity": "Low", "repeat_production_suitable": true, "price_tier": "Entry"}},
    {{"name": "...", "variation_type": "bottom", "description": "...", "production_complexity": "Medium", "repeat_production_suitable": true, "price_tier": "Mid"}}
  ],
  "premium_version": {{"name": "...", "variation_type": "premium", "description": "...", "production_complexity": "High", "repeat_production_suitable": false, "price_tier": "Premium"}},
  "entry_price_version": {{"name": "...", "variation_type": "entry", "description": "...", "production_complexity": "Low", "repeat_production_suitable": true, "price_tier": "Entry"}},
  "content_ideas": [
    {{"format": "Reel", "concept": "...", "description": "..."}},
    {{"format": "Photo", "concept": "...", "description": "..."}},
    {{"format": "Story", "concept": "...", "description": "..."}}
  ]
}}"""

    user_content: list[dict] = [{"type": "text", "text": state["user_input"]}]
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
    result = ExpandedCollection.model_validate_json(resp.choices[0].message.content)
    return {**state, "expand_output": result.model_dump()}


def guardrails_node(state: ExpanderState) -> ExpanderState:
    result = check_guardrails(str(state["expand_output"]))
    return {**state, "guardrails_output": result.model_dump()}


def build_graph() -> Any:
    g = StateGraph(ExpanderState)
    g.add_node("run_expand", expand_collection)
    g.add_node("run_guardrails", guardrails_node)
    g.set_entry_point("run_expand")
    g.add_edge("run_expand", "run_guardrails")
    g.add_edge("run_guardrails", END)
    return g.compile()


graph = build_graph()


def run(user_input: str, image_b64: str | None = None, feedback: str | None = None) -> dict:
    result = graph.invoke({"user_input": user_input, "image_b64": image_b64, "feedback": feedback, "expand_output": None, "guardrails_output": None})
    return {"expanded": result["expand_output"], "guardrails": result["guardrails_output"]}
