from openai import OpenAI
from config import OPENAI_MODEL_FAST
from schemas import GuardrailsResult

_client = OpenAI()

_SYSTEM = """You are the SAMA business guardrails checker. Review the content and flag violations of these rules:

1. Low to medium investment — no suggestions requiring large upfront stock or expensive equipment
2. Reusable patterns — designs should share base patterns where possible
3. Limited dead stock — avoid designs that are hard to sell or too niche
4. Production realism — designs must be stitchable by a boutique atelier, not just beautiful concepts
5. Body-inclusive thinking — silhouettes should flatter multiple body types; adjustable details preferred
6. Trend application — trends must follow: Trend → SAMA interpretation → Commercial application
7. Strong margins — no suggestions that would result in thin margins for a small boutique

Respond with JSON only: {"passed": true/false, "violations": ["..."], "revised_content": "..." or null}"""


def check_guardrails(content: str) -> GuardrailsResult:
    resp = _client.chat.completions.create(
        model=OPENAI_MODEL_FAST,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Check this content:\n\n{content}"},
        ],
        response_format={"type": "json_object"},
    )
    return GuardrailsResult.model_validate_json(resp.choices[0].message.content)
