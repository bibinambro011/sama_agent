from __future__ import annotations

PILLARS = [
    "product",
    "education",
    "storytelling",
    "behind_the_scenes",
    "founder_journey",
    "fashion_inspiration",
    "customer_transformation",
    "styling",
    "sales",
]

# Keyword hints for auto-tagging when LLM doesn't tag
_PILLAR_KEYWORDS: dict[str, list[str]] = {
    "product": ["garment", "fabric", "colour", "design", "piece", "collection", "wear", "outfit", "dress", "kurti", "co-ord"],
    "education": ["how to", "tip", "guide", "care", "measure", "fabric care", "styling tip", "what to wear", "why"],
    "storytelling": ["story", "journey", "behind", "collection story", "inspiration", "mood", "feeling"],
    "behind_the_scenes": ["atelier", "stitching", "fitting", "process", "making", "tailor", "pattern", "cutting"],
    "founder_journey": ["founder", "i decided", "we started", "our story", "why sama", "my vision"],
    "fashion_inspiration": ["trend", "mood board", "colour story", "inspiration", "season", "palette"],
    "customer_transformation": ["customer", "testimonial", "before", "after", "she wore", "transformation"],
    "styling": ["style", "how to wear", "pair with", "three ways", "outfit idea", "combination"],
    "sales": ["order", "pre-order", "book", "dm us", "available", "slots", "reserve", "buy", "shop"],
}


def _tag_text(text: str) -> str | None:
    """Guess pillar from text keywords. Returns pillar name or None."""
    text_lower = text.lower()
    for pillar, keywords in _PILLAR_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return pillar
    return None


def count_pillars(content: dict) -> dict[str, int]:
    """
    Count pillar coverage from content pack.
    Expects reels, captions, stories fields.
    Returns dict of pillar -> count.
    """
    counts: dict[str, int] = {p: 0 for p in PILLARS}

    # Tag reels by concept + hook
    for reel in content.get("reels", []):
        text = f"{reel.get('concept', '')} {reel.get('hook', '')}"
        pillar = _tag_text(text)
        if pillar:
            counts[pillar] += 1

    # Tag captions
    for caption in content.get("captions", []):
        pillar = _tag_text(caption)
        if pillar:
            counts[pillar] += 1

    # Tag stories by type
    stories = content.get("stories", {})
    if stories.get("behind_the_scenes"):
        counts["behind_the_scenes"] += len(stories["behind_the_scenes"])
    if stories.get("polls") or stories.get("questions"):
        counts["education"] += 1
    if stories.get("ordering_prompts"):
        counts["sales"] += len(stories["ordering_prompts"])
    if stories.get("design_voting"):
        counts["product"] += len(stories["design_voting"])

    return counts


def compute_pillar_balance(content: dict) -> dict:
    """
    Compute pillar balance in Python only.
    Returns a dict matching PillarBalance schema.
    """
    counts = count_pillars(content)
    missing = [p for p in PILLARS if counts[p] == 0]
    is_balanced = len(missing) == 0

    if is_balanced:
        note = "All 9 pillars covered."
    else:
        note = f"Needs Adjustment — missing pillars: {', '.join(missing)}"

    return {
        **counts,
        "is_balanced": is_balanced,
        "note": note,
    }
