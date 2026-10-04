import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from schemas import PricingInput
from tools.pricing import calculate_price


def make_input(**kwargs) -> PricingInput:
    defaults = dict(
        fabric_cost=500, stitching_cost=300, trims_and_embellishments=100,
        labour=200, packaging=50, overheads=100, target_margin_pct=50,
        perceived_value_uplift_pct=0,
    )
    defaults.update(kwargs)
    return PricingInput(**defaults)


def test_total_cost():
    result = calculate_price(make_input())
    assert result.total_cost == 1250.0


def test_margin_50_pct():
    result = calculate_price(make_input(target_margin_pct=50))
    assert result.margin_achieved_pct == 50.0


def test_suggested_price_above_cost():
    result = calculate_price(make_input())
    assert result.suggested_price > result.total_cost


def test_price_tiers_ordering():
    result = calculate_price(make_input())
    assert result.entry_price < result.hero_price < result.premium_price


def test_perceived_value_uplift():
    base = calculate_price(make_input(perceived_value_uplift_pct=0))
    uplifted = calculate_price(make_input(perceived_value_uplift_pct=20))
    assert uplifted.suggested_price > base.suggested_price


def test_cost_breakdown_keys():
    result = calculate_price(make_input())
    assert set(result.cost_breakdown.keys()) == {
        "fabric", "stitching", "trims_and_embellishments", "labour", "packaging", "overheads"
    }


def test_zero_overheads():
    result = calculate_price(make_input(overheads=0))
    assert result.total_cost == 1150.0
