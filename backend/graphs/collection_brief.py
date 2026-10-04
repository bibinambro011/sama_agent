from __future__ import annotations
from openai import OpenAI
from config import OPENAI_MODEL
from knowledge_loader import load, build_context_block
from schemas import CollectionBrief

_client = OpenAI()


def generate_brief(user_input: str, feedback: str | None = None) -> CollectionBrief:
    knowledge = load("brand_identity.md", "collection_types.md", "customer_psychology.md", "business_strategy.md")
    context = build_context_block(user_input)
    feedback_block = ""
    if feedback:
        feedback_block = f"\n\n⚠️ OWNER FEEDBACK — apply this precisely:\n{feedback}\n"

    system = f"""You are SAMA's collection brief writer. Create a precise, specific brief that will be the single source of truth for all content generated for this collection.
{feedback_block}
{knowledge}
{context}

Rules:
- hero_garments must have exactly 3 items — each with a unique name, specific fabric, colourway, neckline, sleeve, length, and ONE signature SAMA detail
- palette must have 4 to 5 named colours (specific names, not just "blue" — e.g. "dusty rose", "ivory", "forest green")
- kids_piece must match one of the adult hero garments in fabric or colourway
- signature_details are 2 details that repeat across the whole collection (e.g. "self-fabric bow at back neck", "contrast piping on sleeves")
- story_angle is ONE specific angle for this collection (e.g. "the fitting room moment", "mother and daughter matching")
- fill_these_in lists all placeholders the owner must fill before publishing (dates, prices, specific claims)
- assumptions lists what you assumed when information was missing
- Do NOT suggest sarees, blouses, Anarkalis, or bridal wear
- Do NOT claim handloom, limited stock, or awards unless confirmed in the business profile

Respond with JSON only:
{{
  "occasion": "...",
  "target_customer": "...",
  "price_positioning": "...",
  "assumptions": ["..."],
  "palette": ["colour1", "colour2", "colour3", "colour4"],
  "fabric_direction": "...",
  "hero_garments": [
    {{
      "name": "...",
      "garment_type": "kurti set|co-ord|dress|top|bottom",
      "fabric": "...",
      "colourway": "...",
      "neckline": "...",
      "sleeve": "...",
      "length": "...",
      "signature_detail": "...",
      "production_complexity": "Low|Medium|High",
      "price_tag": "Entry|Hero|Premium"
    }},
    {{...}},
    {{...}}
  ],
  "kids_piece": "...",
  "signature_details": ["detail1", "detail2"],
  "story_angle": "...",
  "fill_these_in": ["[date] — ordering deadline", "[price] — price for hero garment"]
}}"""

    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.7,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_input},
        ],
        response_format={"type": "json_object"},
    )
    return CollectionBrief.model_validate_json(resp.choices[0].message.content)
