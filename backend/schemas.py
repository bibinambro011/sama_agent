from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ── Router ────────────────────────────────────────────────────────────────────

class RouterDecision(BaseModel):
    intent: Literal[
        "collection_planner",
        "fabric_analyzer",
        "design_evaluator",
        "collection_expander",
        "content_generator",
        "launch_planner",
        "pricing",
    ]
    confidence: float = Field(ge=0, le=1)
    reasoning: str


# ── Collection Planner ────────────────────────────────────────────────────────

class DesignIdea(BaseModel):
    garment_type: str
    silhouette: str
    neckline: str
    sleeve: str
    length: str
    fabric: str
    colour: str
    special_detail: str
    styling: str
    occasion: str
    why_customer_buys: str
    production_complexity: Literal["Low", "Medium", "High"]
    repeat_production_suitable: bool


class CollectionDirection(BaseModel):
    name_ideas: list[str]
    core_story: str
    mood: str
    colour_palette: list[str]
    fabric_direction: str
    silhouette_direction: str
    design_language: str
    price_positioning: str
    uniquely_sama: str
    what_it_should_not_become: str


class CollectionPlan(BaseModel):
    assumptions: list[str]
    collection_direction: CollectionDirection
    target_customer: str
    design_ideas: list[DesignIdea]
    fabric_and_colours: str
    content_ideas: list[str]
    launch_strategy: str
    business_strategy: str
    immediate_actions: list[str] = Field(min_length=3, max_length=3)


# ── Fabric Analyzer ───────────────────────────────────────────────────────────

class GarmentConcept(BaseModel):
    name: str
    category: Literal["Elevated Casual", "Formality", "Occasion", "Seasonal"]
    description: str
    why_it_works: str


class FabricAnalysis(BaseModel):
    texture: str
    weight: str
    fall: str
    colour_description: str
    print_description: str
    season_suitability: list[str]
    garment_suitability: list[str]
    collection_suitability: list[str]
    garment_concepts: list[GarmentConcept] = Field(min_length=3, max_length=7)
    recommended_direction: str
    recommended_direction_reason: str


# ── Design Evaluator ──────────────────────────────────────────────────────────

class DesignScores(BaseModel):
    visual_appeal: int = Field(ge=1, le=10)
    sama_brand_fit: int = Field(ge=1, le=10)
    wearability: int = Field(ge=1, le=10)
    comfort: int = Field(ge=1, le=10)
    uniqueness: int = Field(ge=1, le=10)
    customer_appeal: int = Field(ge=1, le=10)
    production_feasibility: int = Field(ge=1, le=10)
    cost_feasibility: int = Field(ge=1, le=10)
    styling_potential: int = Field(ge=1, le=10)
    instagram_potential: int = Field(ge=1, le=10)
    repeat_sale_potential: int = Field(ge=1, le=10)


class DesignEvaluation(BaseModel):
    scores: DesignScores
    overall_score: float
    what_works: list[str]
    what_doesnt: list[str]
    what_to_change: list[str]
    how_to_make_more_sama: list[str]
    how_to_make_more_commercial: list[str]
    retain: list[str]
    modify: list[str]
    sleeve_options: list[str]
    neckline_options: list[str]
    back_options: list[str]
    fabric_suggestions: list[str]
    embellishment_suggestions: list[str]


# ── Collection Expander ───────────────────────────────────────────────────────

class ExpandedPiece(BaseModel):
    name: str
    variation_type: str
    description: str
    production_complexity: Literal["Low", "Medium", "High"]
    repeat_production_suitable: bool
    price_tier: Literal["Entry", "Mid", "Premium"]


class ContentIdea(BaseModel):
    format: Literal["Reel", "Photo", "Story"]
    concept: str
    description: str


class ExpandedCollection(BaseModel):
    base_garment: str
    sleeve_variations: list[ExpandedPiece] = Field(min_length=3, max_length=3)
    neckline_variations: list[ExpandedPiece] = Field(min_length=2, max_length=2)
    colourways: list[ExpandedPiece] = Field(min_length=3, max_length=3)
    bottoms: list[ExpandedPiece]
    premium_version: ExpandedPiece
    entry_price_version: ExpandedPiece
    content_ideas: list[ContentIdea]


# ── Content Generator ─────────────────────────────────────────────────────────

class ReelContent(BaseModel):
    hook: str
    concept: str
    shot_plan: list[str]
    on_screen_text: list[str]
    voiceover: Optional[str]
    caption: str
    cta: str


class PhotoContent(BaseModel):
    product_shots: list[str]
    lifestyle_shots: list[str]
    detail_shots: list[str]
    fabric_shots: list[str]
    styling_combinations: list[str]


class StoryContent(BaseModel):
    polls: list[str]
    questions: list[str]
    behind_the_scenes: list[str]
    design_voting: list[str]
    ordering_prompts: list[str]


class PillarBalance(BaseModel):
    product: int
    education: int
    storytelling: int
    behind_the_scenes: int
    founder_journey: int
    fashion_inspiration: int
    customer_transformation: int
    styling: int
    sales: int
    is_balanced: bool
    note: str


class ContentPack(BaseModel):
    reels: list[ReelContent]
    photos: PhotoContent
    stories: StoryContent
    captions: list[str]
    pillar_balance: PillarBalance


# tone and banned phrase results are added at the API layer, not in the LLM schema


# ── Launch Planner ────────────────────────────────────────────────────────────

class LaunchDay(BaseModel):
    day_offset: int          # -21 to +7
    date_label: str          # e.g. "T-21"
    phase: str
    content_item: str
    platform: str
    notes: str


class LaunchPlan(BaseModel):
    collection_name: str
    timeline: list[LaunchDay]


# ── Pricing ───────────────────────────────────────────────────────────────────

class PricingInput(BaseModel):
    fabric_cost: float
    stitching_cost: float
    trims_and_embellishments: float
    labour: float
    packaging: float
    overheads: float
    target_margin_pct: float = Field(ge=0, le=100)
    perceived_value_uplift_pct: float = Field(default=0, ge=0, le=100)


class PricingOutput(BaseModel):
    total_cost: float
    suggested_price: float
    entry_price: float
    hero_price: float
    premium_price: float
    margin_achieved_pct: float
    cost_breakdown: dict[str, float]


# ── Memory / Saved Items ──────────────────────────────────────────────────────

class SavedItem(BaseModel):
    id: int
    item_type: str
    title: str
    content: str          # JSON string of the result
    feedback: Optional[str]
    created_at: str


# ── Guardrails ────────────────────────────────────────────────────────────────

class GuardrailsResult(BaseModel):
    passed: bool
    violations: list[str]
    revised_content: Optional[str]


# ── Tone Checker ──────────────────────────────────────────────────────────────

class ToneResult(BaseModel):
    passed: bool
    flags: list[str]
    revised_text: Optional[str]


# ── Business Profile ──────────────────────────────────────────────────────────

class BusinessProfile(BaseModel):
    location_climate: str = ""
    categories_made: list[str] = []
    categories_not_made: list[str] = []
    fabric_families_used: list[str] = []
    fabrics_to_avoid: list[str] = []
    price_range: dict[str, str] = {}
    stitching_lead_time_days: int = 21
    monthly_capacity: str = ""
    size_range: str = ""
    custom_measurements: bool = True
    sales_channels: list[str] = []
    confirmed_facts: list[str] = []
    never_claim: list[str] = []
    caption_languages: list[str] = ["English"]


# ── Rules ─────────────────────────────────────────────────────────────────────

class Rule(BaseModel):
    id: Optional[int] = None
    scope: Literal["global", "collection"]
    occasion: Optional[str] = None
    rule_text: str
    created_at: Optional[str] = None
    active: bool = True


# ── Banned Phrase ─────────────────────────────────────────────────────────────

class BannedPhrase(BaseModel):
    id: Optional[int] = None
    phrase: str
    active: bool = True


# ── Validator Result ──────────────────────────────────────────────────────────

class ValidatorResult(BaseModel):
    passed: bool
    banned_phrase_hits: list[str] = []
    warnings: list[str] = []
