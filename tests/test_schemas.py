import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from schemas import (
    PricingInput, PricingOutput, CollectionPlan, RouterDecision,
    DesignScores, ToneResult, GuardrailsResult,
)


def test_pricing_input_valid():
    p = PricingInput(
        fabric_cost=500, stitching_cost=300, trims_and_embellishments=100,
        labour=200, packaging=50, overheads=100, target_margin_pct=50,
    )
    assert p.target_margin_pct == 50


def test_pricing_input_margin_bounds():
    import pytest
    with pytest.raises(Exception):
        PricingInput(
            fabric_cost=100, stitching_cost=100, trims_and_embellishments=0,
            labour=0, packaging=0, overheads=0, target_margin_pct=110,
        )


def test_router_decision_valid():
    r = RouterDecision(intent="collection_planner", confidence=0.95, reasoning="User asked for a collection")
    assert r.intent == "collection_planner"


def test_router_decision_invalid_intent():
    import pytest
    with pytest.raises(Exception):
        RouterDecision(intent="unknown_intent", confidence=0.5, reasoning="test")


def test_design_scores_bounds():
    import pytest
    with pytest.raises(Exception):
        DesignScores(
            visual_appeal=11, sama_brand_fit=5, wearability=5, comfort=5,
            uniqueness=5, customer_appeal=5, production_feasibility=5,
            cost_feasibility=5, styling_potential=5, instagram_potential=5,
            repeat_sale_potential=5,
        )


def test_tone_result_valid():
    t = ToneResult(passed=True, flags=[], revised_text=None)
    assert t.passed is True


def test_guardrails_result_valid():
    g = GuardrailsResult(passed=False, violations=["Too expensive"], revised_content="revised")
    assert len(g.violations) == 1
