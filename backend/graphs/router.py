from __future__ import annotations
from openai import OpenAI
from config import OPENAI_MODEL_FAST
from schemas import RouterDecision

_client = OpenAI()

_SYSTEM = """You are the SAMA Agent router. Classify the user's request into exactly one intent.

Intents:
- collection_planner: planning a collection, season, occasion, festival (Onam, Diwali, etc.)
- fabric_analyzer: analyzing a fabric, material, textile
- design_evaluator: evaluating, scoring, critiquing a design or garment
- collection_expander: expanding one garment into a full mini collection
- content_generator: creating Instagram content, reels, captions, stories, photos
- launch_planner: planning a launch timeline, schedule, rollout
- pricing: calculating price, cost, margin

Respond with JSON only: {"intent": "...", "confidence": 0.0, "reasoning": "..."}"""


def route(user_input: str, has_image: bool = False) -> RouterDecision:
    context = user_input
    if has_image:
        context += "\n[User has uploaded an image]"

    resp = _client.chat.completions.create(
        model=OPENAI_MODEL_FAST,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": context},
        ],
        response_format={"type": "json_object"},
    )
    return RouterDecision.model_validate_json(resp.choices[0].message.content)
