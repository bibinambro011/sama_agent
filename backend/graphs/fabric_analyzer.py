from __future__ import annotations
from typing import TypedDict, Any
from openai import OpenAI
from langgraph.graph import StateGraph, END
from config import OPENAI_MODEL
from knowledge_loader import load, build_context_block
from schemas import FabricAnalysis
from tools.guardrails import check_guardrails

_client = OpenAI()


def _feedback_block(feedback: str | None) -> str:
    if not feedback:
        return ""
    return f"\n\n⚠️ OWNER FEEDBACK — apply this precisely before anything else:\n{feedback}\n"


class FabricState(TypedDict):
    user_input: str
    image_b64: str | None
    feedback: str | None
    fabric_output: dict[str, Any] | None
    guardrails_output: dict[str, Any] | None


def analyze_fabric(state: FabricState) -> FabricState:
    knowledge = load("brand_identity.md", "collection_types.md", "customer_psychology.md")
    context = build_context_block(state["user_input"] or "")
    system = f"""You are SAMA's fabric analysis expert. Analyze the fabric and suggest garment concepts.
{_feedback_block(state.get('feedback'))}
{knowledge}
{context}

Respond with JSON only. garment_concepts MUST contain exactly 5 objects — do not return fewer:
{{
  "texture": "...", "weight": "...", "fall": "...", "colour_description": "...", "print_description": "...",
  "season_suitability": ["...", "..."], "garment_suitability": ["...", "..."], "collection_suitability": ["...", "..."],
  "garment_concepts": [
    {{"name": "...", "category": "Elevated Casual", "description": "...", "why_it_works": "..."}},
    {{"name": "...", "category": "Formality", "description": "...", "why_it_works": "..."}},
    {{"name": "...", "category": "Occasion", "description": "...", "why_it_works": "..."}},
    {{"name": "...", "category": "Seasonal", "description": "...", "why_it_works": "..."}},
    {{"name": "...", "category": "Elevated Casual", "description": "...", "why_it_works": "..."}}
  ],
  "recommended_direction": "...", "recommended_direction_reason": "..."
}}"""

    user_content: list[dict] = [{"type": "text", "text": state["user_input"] or "Analyze this fabric."}]
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
    result = FabricAnalysis.model_validate_json(resp.choices[0].message.content)
    return {**state, "fabric_output": result.model_dump()}


def guardrails_node(state: FabricState) -> FabricState:
    result = check_guardrails(str(state["fabric_output"]))
    return {**state, "guardrails_output": result.model_dump()}


def build_graph() -> Any:
    g = StateGraph(FabricState)
    g.add_node("run_analyze", analyze_fabric)
    g.add_node("run_guardrails", guardrails_node)
    g.set_entry_point("run_analyze")
    g.add_edge("run_analyze", "run_guardrails")
    g.add_edge("run_guardrails", END)
    return g.compile()


graph = build_graph()


def run(user_input: str, image_b64: str | None = None, feedback: str | None = None) -> dict:
    result = graph.invoke({"user_input": user_input, "image_b64": image_b64, "feedback": feedback, "fabric_output": None, "guardrails_output": None})
    return {"analysis": result["fabric_output"], "guardrails": result["guardrails_output"]}
