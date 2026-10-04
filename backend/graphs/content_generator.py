from __future__ import annotations
from typing import TypedDict, Any
from openai import OpenAI
from langgraph.graph import StateGraph, END
from config import OPENAI_MODEL
from knowledge_loader import load, build_context_block
from schemas import ContentPack, CollectionBrief
from tools.tone_checker import apply_tone_fix_to_pack
from tools.guardrails import check_guardrails
from tools.banned_phrases import assert_no_banned_phrases
from tools.pillar_counter import compute_pillar_balance

_client = OpenAI()


def _feedback_block(feedback: str | None) -> str:
    if not feedback:
        return ""
    return f"\n\n⚠️ OWNER FEEDBACK — apply this precisely before anything else:\n{feedback}\n"


def _brief_block(brief: dict | None) -> str:
    if not brief:
        return ""
    garments = brief.get("hero_garments", [])
    garment_lines = "\n".join(
        f"  - {g['name']}: {g['garment_type']}, {g['fabric']}, {g['colourway']}, "
        f"{g['neckline']} neckline, {g['sleeve']} sleeve, {g['length']}, "
        f"signature detail: {g['signature_detail']}"
        for g in garments
    )
    return f"""
## Collection Brief — USE THIS AS YOUR ONLY SOURCE OF TRUTH
Occasion: {brief.get('occasion')}
Story angle: {brief.get('story_angle')}
Palette: {', '.join(brief.get('palette', []))}
Fabric direction: {brief.get('fabric_direction')}
Signature details (repeat across all content): {', '.join(brief.get('signature_details', []))}

Hero garments (use THESE EXACT NAMES in all reels, captions, photos, stories):
{garment_lines}

Kids piece: {brief.get('kids_piece')}

RULE: Every reel, caption, and photo idea must reference at least one of the hero garments by name.
RULE: Do not invent garments not listed above.
"""


def _validate_garment_names(content: dict, brief: dict | None) -> list[str]:
    """Check that content references the brief's garment names, not invented ones."""
    if not brief:
        return []
    garment_names = {g["name"].lower() for g in brief.get("hero_garments", [])}
    if not garment_names:
        return []

    warnings = []
    all_text = " ".join([
        " ".join(content.get("captions", [])),
        " ".join(r.get("caption", "") + " " + r.get("concept", "") for r in content.get("reels", [])),
    ]).lower()

    found_any = any(name in all_text for name in garment_names)
    if not found_any:
        warnings.append(
            f"No hero garment names found in content. Expected one of: {', '.join(brief.get('hero_garments', [{}])[i].get('name', '') for i in range(len(brief.get('hero_garments', []))))}"
        )
    return warnings


class ContentState(TypedDict):
    user_input: str
    request_type: str
    feedback: str | None
    brief: dict | None
    content_output: dict[str, Any] | None
    tone_output: dict[str, Any] | None
    guardrails_output: dict[str, Any] | None


def generate_content(state: ContentState) -> ContentState:
    knowledge = load("brand_identity.md", "content_strategy.md", "tone_of_voice.md", "customer_psychology.md")
    context = build_context_block(state["user_input"])
    brief_block = _brief_block(state.get("brief"))

    system = f"""You are SAMA's content creation expert. Create Instagram content that is elegant, warm, and on-brand.
{_feedback_block(state.get('feedback'))}
{knowledge}
{context}
{brief_block}

Content request type: {state['request_type']}
Rules:
- Sales posts must not exceed 25% of total content
- Maximum 1 emoji per caption, zero emojis in hooks
- Every caption must name a specific garment detail (sleeve shape, neckline, fabric, colour)
- Every reel and caption must reference at least one hero garment by its exact name from the brief
- No generic phrases — every line must be specific to SAMA and this collection

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
    output["pillar_balance"] = compute_pillar_balance(output)
    return {**state, "content_output": output}


def tone_check_node(state: ContentState) -> ContentState:
    fixed, all_flags, still_failing = apply_tone_fix_to_pack(state["content_output"])
    tone_output = {
        "passed": len(all_flags) == 0,
        "flags": all_flags,
        "still_failing_fields": still_failing,
        "revised_text": None,
    }
    return {**state, "content_output": fixed, "tone_output": tone_output}


def banned_phrases_node(state: ContentState) -> ContentState:
    hits = assert_no_banned_phrases(state["content_output"])
    tone = state.get("tone_output") or {}
    tone["banned_phrase_hits"] = hits
    garment_warnings = _validate_garment_names(state["content_output"], state.get("brief"))
    tone["garment_warnings"] = garment_warnings
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


def run(user_input: str, request_type: str = "full content pack", feedback: str | None = None, brief: dict | None = None) -> dict:
    result = graph.invoke({
        "user_input": user_input,
        "request_type": request_type,
        "feedback": feedback,
        "brief": brief,
        "content_output": None,
        "tone_output": None,
        "guardrails_output": None,
    })
    return {
        "content": result["content_output"],
        "tone": result["tone_output"],
        "guardrails": result["guardrails_output"],
    }
