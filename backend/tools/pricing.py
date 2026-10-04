from schemas import PricingInput, PricingOutput


def calculate_price(inp: PricingInput) -> PricingOutput:
    """Pure Python pricing calculator — no LLM involved."""
    total_cost = (
        inp.fabric_cost
        + inp.stitching_cost
        + inp.trims_and_embellishments
        + inp.labour
        + inp.packaging
        + inp.overheads
    )
    margin_multiplier = 1 / (1 - inp.target_margin_pct / 100)
    base_price = total_cost * margin_multiplier
    uplift_multiplier = 1 + inp.perceived_value_uplift_pct / 100
    suggested_price = round(base_price * uplift_multiplier, 2)

    entry_price = round(suggested_price * 0.85, 2)
    hero_price = suggested_price
    premium_price = round(suggested_price * 1.3, 2)

    margin_achieved = round((1 - total_cost / suggested_price) * 100, 2)

    return PricingOutput(
        total_cost=round(total_cost, 2),
        suggested_price=suggested_price,
        entry_price=entry_price,
        hero_price=hero_price,
        premium_price=premium_price,
        margin_achieved_pct=margin_achieved,
        cost_breakdown={
            "fabric": inp.fabric_cost,
            "stitching": inp.stitching_cost,
            "trims_and_embellishments": inp.trims_and_embellishments,
            "labour": inp.labour,
            "packaging": inp.packaging,
            "overheads": inp.overheads,
        },
    )
