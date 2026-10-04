from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def load(*filenames: str) -> str:
    """Load and concatenate knowledge markdown files."""
    parts = []
    for name in filenames:
        path = KNOWLEDGE_DIR / name
        if path.exists():
            parts.append(path.read_text())
    return "\n\n---\n\n".join(parts)
