from __future__ import annotations
import base64
import csv
import io
import json
import time
from typing import Any
from PIL import Image

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from memory.db import (
    init_db, save_item, get_items, get_item, update_feedback, delete_item, save_style_memory,
    get_business_profile, save_business_profile,
    add_rule, get_rules, get_all_rules, toggle_rule, delete_rule,
    get_banned_phrases, add_banned_phrase, toggle_banned_phrase, delete_banned_phrase,
    get_generation_logs,
    save_brief, get_brief, approve_brief, get_latest_approved_brief,
)
from schemas import PricingInput, BusinessProfile, Rule, BannedPhrase, CollectionBrief
from graphs.collection_brief import generate_brief
from tools.pricing import calculate_price
from graphs.router import route
import graphs.collection_planner as collection_planner
import graphs.fabric_analyzer as fabric_analyzer
import graphs.design_evaluator as design_evaluator
import graphs.collection_expander as collection_expander
import graphs.content_generator as content_generator
import graphs.launch_planner as launch_planner

app = FastAPI(title="SAMA Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ── Router / Chat endpoint ────────────────────────────────────────────────────

def _normalize_image_b64(image_b64: str | None) -> str | None:
    """Convert any image format to JPEG base64 for OpenAI compatibility."""
    if not image_b64:
        return None
    raw = base64.b64decode(image_b64)
    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        # Try pillow-avif-plugin for AVIF support
        try:
            import pillow_avif  # noqa: F401
            img = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Unsupported image format. Please upload PNG, JPEG, WEBP, or GIF. Error: {e}")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


class ChatRequest(BaseModel):
    message: str
    image_b64: str | None = None
    request_type: str | None = None
    feedback: str | None = None
    brief_id: int | None = None  # optional: use an approved brief for content generation


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict[str, Any]:
    image_b64 = _normalize_image_b64(req.image_b64)
    decision = route(req.message, has_image=bool(image_b64))
    intent = decision.intent

    try:
        if intent == "collection_planner":
            result = collection_planner.run(req.message, req.feedback)
        elif intent == "fabric_analyzer":
            result = fabric_analyzer.run(req.message, image_b64, req.feedback)
        elif intent == "design_evaluator":
            result = design_evaluator.run(req.message, image_b64, req.feedback)
        elif intent == "collection_expander":
            result = collection_expander.run(req.message, image_b64, req.feedback)
        elif intent == "content_generator":
            brief = None
            if req.brief_id:
                brief_row = get_brief(req.brief_id)
                brief = brief_row["brief"] if brief_row else None
            result = content_generator.run(req.message, req.request_type or "full content pack", req.feedback, brief)
        elif intent == "launch_planner":
            result = launch_planner.run(req.message, req.feedback)
        elif intent == "pricing":
            return {"intent": intent, "message": "Please use the Pricing Calculator form for pricing calculations."}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"intent": intent, "result": result}


# ── Pricing ───────────────────────────────────────────────────────────────────

@app.post("/api/pricing")
def pricing(inp: PricingInput) -> dict[str, Any]:
    result = calculate_price(inp)
    return result.model_dump()


# ── Memory / Saved Items ──────────────────────────────────────────────────────

class SaveRequest(BaseModel):
    item_type: str
    title: str
    content: dict[str, Any]
    feedback: str | None = None


@app.post("/api/save")
def save(req: SaveRequest) -> dict:
    item_id = save_item(req.item_type, req.title, req.content, req.feedback)
    save_style_memory(req.item_type, req.title)
    return {"id": item_id, "message": "Saved successfully"}


@app.get("/api/saved")
def list_saved(item_type: str | None = None) -> list[dict]:
    return get_items(item_type)


@app.get("/api/saved/{item_id}")
def get_saved(item_id: int) -> dict:
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/api/saved/{item_id}/feedback")
def add_feedback(item_id: int, feedback: str = Form(...)) -> dict:
    update_feedback(item_id, feedback)
    return {"message": "Feedback saved"}


@app.delete("/api/saved/{item_id}")
def remove_saved(item_id: int) -> dict:
    delete_item(item_id)
    return {"message": "Deleted"}


# ── CSV Export for Launch Plan ────────────────────────────────────────────────

@app.get("/api/saved/{item_id}/export-csv")
def export_csv(item_id: int):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    content = json.loads(item["content"])
    plan = content.get("plan", {})
    timeline = plan.get("timeline", [])

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["day_offset", "date_label", "phase", "content_item", "platform", "notes"])
    writer.writeheader()
    writer.writerows(timeline)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=launch_plan_{item_id}.csv"},
    )


# ── Business Profile ──────────────────────────────────────────────────────────────

@app.get("/api/profile")
def get_profile() -> dict:
    profile = get_business_profile()
    return profile or {}


@app.post("/api/profile")
def upsert_profile(profile: BusinessProfile) -> dict:
    save_business_profile(profile.model_dump())
    return {"message": "Profile saved"}


# ── Rules ───────────────────────────────────────────────────────────────────────

@app.get("/api/rules")
def list_rules(occasion: str | None = None) -> list[dict]:
    return get_all_rules() if occasion is None else get_rules(occasion)


@app.post("/api/rules")
def create_rule(rule: Rule) -> dict:
    rule_id = add_rule(rule.scope, rule.rule_text, rule.occasion)
    return {"id": rule_id, "message": "Rule saved"}


@app.patch("/api/rules/{rule_id}")
def patch_rule(rule_id: int, active: bool) -> dict:
    toggle_rule(rule_id, active)
    return {"message": "Updated"}


@app.delete("/api/rules/{rule_id}")
def remove_rule(rule_id: int) -> dict:
    delete_rule(rule_id)
    return {"message": "Deleted"}


# ── Banned Phrases ─────────────────────────────────────────────────────────────

@app.get("/api/banned-phrases")
def list_banned_phrases() -> list[dict]:
    return get_banned_phrases(active_only=False)


@app.post("/api/banned-phrases")
def create_banned_phrase(bp: BannedPhrase) -> dict:
    phrase_id = add_banned_phrase(bp.phrase)
    return {"id": phrase_id, "message": "Added"}


@app.patch("/api/banned-phrases/{phrase_id}")
def patch_banned_phrase(phrase_id: int, active: bool) -> dict:
    toggle_banned_phrase(phrase_id, active)
    return {"message": "Updated"}


@app.delete("/api/banned-phrases/{phrase_id}")
def remove_banned_phrase(phrase_id: int) -> dict:
    delete_banned_phrase(phrase_id)
    return {"message": "Deleted"}


# ── Generation Logs ─────────────────────────────────────────────────────────────

@app.get("/api/logs")
def list_logs(limit: int = 50) -> list[dict]:
    return get_generation_logs(limit)


# ── Collection Brief ────────────────────────────────────────────────────────────

class BriefRequest(BaseModel):
    message: str
    feedback: str | None = None


@app.post("/api/brief")
def create_brief(req: BriefRequest) -> dict:
    try:
        brief = generate_brief(req.message, req.feedback)
        brief_id = save_brief(brief.occasion, brief.model_dump())
        return {"id": brief_id, "brief": brief.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/brief/{brief_id}")
def fetch_brief(brief_id: int) -> dict:
    row = get_brief(brief_id)
    if not row:
        raise HTTPException(status_code=404, detail="Brief not found")
    return row


@app.post("/api/brief/{brief_id}/approve")
def approve_brief_endpoint(brief_id: int) -> dict:
    approve_brief(brief_id)
    return {"message": "Brief approved"}
