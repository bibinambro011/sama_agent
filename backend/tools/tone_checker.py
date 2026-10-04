from openai import OpenAI
from config import OPENAI_MODEL_FAST
from schemas import ToneResult

_client = OpenAI()

_SYSTEM = """You are the SAMA tone checker. SAMA's tone is: elegant, warm, intelligent, feminine, contemporary, confident.

Flag and rewrite content that has ANY of:
- Cheap-sounding sales language (e.g. "Hurry! Order NOW!")
- Excessive luxury jargon (e.g. "draped in the finest silks, this masterpiece...")
- Overly dramatic captions
- Generic motivational quotes
- More than 2 emojis
- Clichés: "where elegance meets sophistication", "redefining fashion", "timeless elegance", "effortlessly chic", "luxury at its finest", "for the modern woman"

Respond with JSON only: {"passed": true/false, "flags": ["..."], "revised_text": "..." or null}"""


def check_tone(text: str) -> ToneResult:
    resp = _client.chat.completions.create(
        model=OPENAI_MODEL_FAST,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Check this text:\n\n{text}"},
        ],
        response_format={"type": "json_object"},
    )
    return ToneResult.model_validate_json(resp.choices[0].message.content)
