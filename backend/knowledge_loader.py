from __future__ import annotations
import json
from pathlib import Path
from memory.db import get_business_profile, get_rules

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
OCCASIONS_DIR = KNOWLEDGE_DIR / "occasions"

# Map common user-facing names to occasion filenames
_OCCASION_MAP: dict[str, str] = {
    "onam": "onam.md",
    "christmas": "christmas.md",
    "xmas": "christmas.md",
    "diwali": "diwali.md",
    "deepavali": "diwali.md",
    "eid": "eid.md",
    "eid al-fitr": "eid.md",
    "eid al-adha": "eid.md",
    "vishu": "vishu.md",
    "wedding": "wedding_season.md",
    "wedding season": "wedding_season.md",
    "summer": "summer.md",
    "monsoon": "monsoon.md",
    "rain": "monsoon.md",
    "winter": "winter.md",
    "valentine": "valentines_day.md",
    "valentines day": "valentines_day.md",
    "valentine's day": "valentines_day.md",
    "date night": "valentines_day.md",
    "mothers day": "mothers_day.md",
    "mother's day": "mothers_day.md",
    "back to school": "back_to_school.md",
    "school": "back_to_school.md",
}


def load(*filenames: str) -> str:
    """Load and concatenate knowledge markdown files."""
    parts = []
    for name in filenames:
        path = KNOWLEDGE_DIR / name
        if path.exists():
            parts.append(path.read_text())
    return "\n\n---\n\n".join(parts)


def detect_occasion(text: str) -> str | None:
    """Detect occasion name from free text. Returns canonical name or None."""
    text_lower = text.lower()
    for key in _OCCASION_MAP:
        if key in text_lower:
            return key
    return None


def load_occasion_facts(occasion: str | None) -> str:
    """Load occasion fact sheet markdown. Returns empty string if not found."""
    if not occasion:
        return ""
    filename = _OCCASION_MAP.get(occasion.lower())
    if not filename:
        return ""
    path = OCCASIONS_DIR / filename
    if not path.exists():
        return ""
    return path.read_text()


def build_profile_block() -> str:
    """Load business profile from DB and format as a prompt block."""
    profile = get_business_profile()
    if not profile:
        return (
            "\n\n## Business Profile\n"
            "No business profile configured yet. "
            "Make no assumptions about what SAMA does or does not make. "
            "State any assumptions you make explicitly in the output.\n"
        )
    lines = ["", "## Business Profile"]
    if profile.get("location_climate"):
        lines.append(f"- Location/climate: {profile['location_climate']}")
    if profile.get("categories_made"):
        lines.append(f"- Makes: {', '.join(profile['categories_made'])}")
    if profile.get("categories_not_made"):
        lines.append(f"- Does NOT make: {', '.join(profile['categories_not_made'])}")
    if profile.get("fabric_families_used"):
        lines.append(f"- Fabrics used: {', '.join(profile['fabric_families_used'])}")
    if profile.get("fabrics_to_avoid"):
        lines.append(f"- Fabrics to avoid: {', '.join(profile['fabrics_to_avoid'])}")
    if profile.get("confirmed_facts"):
        lines.append(f"- Confirmed facts (may mention): {', '.join(profile['confirmed_facts'])}")
    if profile.get("never_claim"):
        lines.append(f"- NEVER claim: {', '.join(profile['never_claim'])}")
    if profile.get("caption_languages"):
        lines.append(f"- Caption languages: {', '.join(profile['caption_languages'])}")
    if profile.get("size_range"):
        lines.append(f"- Size range: {profile['size_range']}")
    if profile.get("custom_measurements") is not None:
        lines.append(f"- Custom measurements: {'yes' if profile['custom_measurements'] else 'no'}")
    return "\n".join(lines) + "\n"


def build_rules_block(occasion: str | None) -> str:
    """Load active rules for this occasion and format as a prompt block."""
    rules = get_rules(occasion)
    if not rules:
        return ""
    lines = ["", "## Owner Rules — You MUST follow every rule below:"]
    for r in rules:
        scope_label = "GLOBAL" if r["scope"] == "global" else f"COLLECTION ({r['occasion']})"
        lines.append(f"- [{scope_label}] {r['rule_text']}")
    return "\n".join(lines) + "\n"


def build_context_block(user_input: str) -> str:
    """
    Build the full context block: profile + rules + occasion facts.
    Detects occasion from user_input automatically.
    """
    occasion = detect_occasion(user_input)
    profile_block = build_profile_block()
    rules_block = build_rules_block(occasion)
    occasion_block = ""
    if occasion:
        facts = load_occasion_facts(occasion)
        if facts:
            occasion_block = f"\n\n## Occasion Facts — {occasion.title()}\n{facts}\n"
        else:
            occasion_block = (
                f"\n\n## Occasion Facts\n"
                f"No fact sheet found for '{occasion}'. "
                f"State your assumptions about this occasion explicitly in the output.\n"
            )
    return profile_block + rules_block + occasion_block
