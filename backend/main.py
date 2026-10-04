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

from memory.db import init_db, save_item, get_items, get_item, update_feedback, delete_item, save_style_memory
from schemas import PricingInput
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
            result = content_generator.run(req.message, req.request_type or "full content pack", req.feedback)
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
