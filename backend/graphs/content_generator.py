from __future__ import annotations
from typing import TypedDict, Any
from openai import OpenAI
from langgraph.graph import StateGraph, END
from config import OPENAI_MODEL
from knowledge_loader import load, build_context_block
from schemas import ContentPack
from tools.tone_checker import apply_tone_fix_to_pack
from tools.guardrails import check_guardrails
from tools.banned_phrases import assert_no_banned_phrases
from tools.pillar_counter import compute_pillar_balance

_client = OpenAI()


def _feedback_block(feedback: str | None) -> str:
    if not feedback:
        return ""
    return f"\n\n⚠️ OWNER FEEDBACK — apply this precisely before anything else:\n{feedback}\n"


class ContentState(TypedDict):
    user_input: str
    request_type: str
    feedback: str | None
    content_output: dict[str, Any] | None
    tone_output: dict[str, Any] | None
    guardrails_output: dict[str, Any] | None


def generate_content(state: ContentState) -> ContentState:
    knowledge = load("brand_identity.md", "content_strategy.md", "tone_of_voice.md", "customer_psychology.md")
    context = build_context_block(state["user_input"])
    system = f"""You are SAMA's content creation expert. Create Instagram content that is elegant, warm, and on-brand.
{_feedback_block(state.get('feedback'))}
{knowledge}
{context}

Content request type: {state['request_type']}
Rules:
- Sales posts must not exceed 25% of total content
- Maximum 1 emoji per caption, zero emojis in hooks
- Every caption must name a specific garment detail (sleeve shape, neckline, fabric, colour)
- No generic phrases — every line must be specific to SAMA

Respond with JSON only:
{{
  "reels": [{{
    "hook": "...", "concept": "...", "shot_plan": ["..."], "on_screen_text": ["..."],
    "voiceover": "..." or null, "caption": "...", "cta": "..."
  }}],
  "photos": {{
    "product_shots": ["..."], "lifestyle_shots": ["..."], "detail_shots": ["..."],
    "fabric_shots": ["..."], "styling_combinations": ["..."]
  }},
  "stories": {{
    "polls": ["..."], "questions": ["..."], "behind_the_scenes": ["..."],
    "design_voting": ["..."], "ordering_prompts": ["..."]
  }},
  "captions": ["..."],
  "pillar_balance": {{
    "product": 0, "education": 0, "storytelling": 0, "behind_the_scenes": 0,
    "founder_journey": 0, "fashion_inspiration": 0, "customer_transformation": 0,
    "styling": 0, "sales": 0, "is_balanced": true, "note": "..."
  }}
}}"""

    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": state["user_input"]},
        ],
        response_format={"type": "json_object"},
    )
    result = ContentPack.model_validate_json(resp.choices[0].message.content)
    output = result.model_dump()

    # Override pillar_balance with Python-computed values — never trust LLM counts
    output["pillar_balance"] = compute_pillar_balance(output)

    return {**state, "content_output": output}


def tone_check_node(state: ContentState) -> ContentState:
    fixed, all_flags, still_failing = apply_tone_fix_to_pack(state["content_output"])
    tone_output = {
        "passed": len(all_flags) == 0,
        "flags": all_flags,
        "still_failing_fields": still_failing,
        "revised_text": None,  # kept for schema compat
    }
    return {**state, "content_output": fixed, "tone_output": tone_output}


def banned_phrases_node(state: ContentState) -> ContentState:
    hits = assert_no_banned_phrases(state["content_output"])
    # Attach hits to tone_output for reporting — don't crash, just flag
    tone = state.get("tone_output") or {}
    tone["banned_phrase_hits"] = hits
    if hits:
        tone["passed"] = False
    return {**state, "tone_output": tone}


def guardrails_node(state: ContentState) -> ContentState:
    result = check_guardrails(str(state["content_output"]))
    return {**state, "guardrails_output": result.model_dump()}


def build_graph() -> Any:
    g = StateGraph(ContentState)
    g.add_node("run_generate", generate_content)
    g.add_node("run_tone_check", tone_check_node)
    g.add_node("run_banned_phrases", banned_phrases_node)
    g.add_node("run_guardrails", guardrails_node)
    g.set_entry_point("run_generate")
    g.add_edge("run_generate", "run_tone_check")
    g.add_edge("run_tone_check", "run_banned_phrases")
    g.add_edge("run_banned_phrases", "run_guardrails")
    g.add_edge("run_guardrails", END)
    return g.compile()


graph = build_graph()


def run(user_input: str, request_type: str = "full content pack", feedback: str | None = None) -> dict:
    result = graph.invoke({
        "user_input": user_input,
        "request_type": request_type,
        "feedback": feedback,
        "content_output": None,
        "tone_output": None,
        "guardrails_output": None,
    })
    return {
        "content": result["content_output"],
        "tone": result["tone_output"],
        "guardrails": result["guardrails_output"],
    }
