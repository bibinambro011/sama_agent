from __future__ import annotations
from openai import OpenAI
from config import OPENAI_MODEL_FAST
from schemas import ToneResult

_client = OpenAI()

_SYSTEM = """You are the SAMA tone checker. SAMA's tone is: elegant, warm, intelligent, feminine, contemporary, confident.

Flag content that has ANY of:
- Cheap-sounding sales language (e.g. "Hurry! Order NOW!", "Don't miss out!")
- Excessive luxury jargon (e.g. "draped in the finest silks, this masterpiece...")
- Overly dramatic captions (e.g. "She walked in and the room fell silent")
- Generic motivational quotes unrelated to the garment
- More than 1 emoji in a caption, or any emoji in a hook
- Clichés (see banned list in system context)

For each flag, quote the EXACT phrase that is problematic.
Then rewrite the ENTIRE text with all flagged phrases fixed.

Respond with JSON only:
{
  "passed": true or false,
  "flags": ["exact phrase 1", "exact phrase 2"],
  "revised_text": "full rewritten text with all fixes applied, or null if passed"
}"""


def check_tone(text: str) -> ToneResult:
    resp = _client.chat.completions.create(
        model=OPENAI_MODEL_FAST,
        temperature=0.2,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Check this text:\n\n{text}"},
        ],
        response_format={"type": "json_object"},
    )
    return ToneResult.model_validate_json(resp.choices[0].message.content)


def check_and_fix_tone(text: str, max_loops: int = 3) -> tuple[str, list[str], bool]:
    """
    Run tone check loop up to max_loops times.
    Returns (final_text, all_flags_found, still_failing).
    still_failing=True means it failed even after max_loops.
    """
    all_flags: list[str] = []
    current = text

    for _ in range(max_loops):
        result = check_tone(current)
        if result.passed:
            return current, all_flags, False
        all_flags.extend(result.flags)
        if result.revised_text:
            current = result.revised_text
        else:
            # LLM flagged but gave no rewrite — stop
            break

    return current, all_flags, True


def apply_tone_fix_to_pack(content: dict, max_loops: int = 3) -> tuple[dict, list[str], list[str]]:
    """
    Apply tone fix to all text fields in a content pack.
    Fixes captions, reel hooks, reel captions, and on_screen_text in place.
    Returns (fixed_content, all_flags, still_failing_fields).
    """
    import copy
    fixed = copy.deepcopy(content)
    all_flags: list[str] = []
    still_failing: list[str] = []

    # Fix captions list
    fixed_captions = []
    for i, caption in enumerate(fixed.get("captions", [])):
        text, flags, failed = check_and_fix_tone(caption, max_loops)
        fixed_captions.append(text)
        all_flags.extend(flags)
        if failed:
            still_failing.append(f"caption[{i}]")
    fixed["captions"] = fixed_captions

    # Fix reel hooks and captions
    for i, reel in enumerate(fixed.get("reels", [])):
        if reel.get("hook"):
            text, flags, failed = check_and_fix_tone(reel["hook"], max_loops)
            reel["hook"] = text
            all_flags.extend(flags)
            if failed:
                still_failing.append(f"reel[{i}].hook")

        if reel.get("caption"):
            text, flags, failed = check_and_fix_tone(reel["caption"], max_loops)
            reel["caption"] = text
            all_flags.extend(flags)
            if failed:
                still_failing.append(f"reel[{i}].caption")

    return fixed, all_flags, still_failing
