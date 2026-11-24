from dataclasses import dataclass


@dataclass
class GradingROIResult:
    gem_net_gain: float
    psa9_salvage_net: float
    expected_net_profit: float
    roi_on_grading_fee_pct: float
    verdict: str


def calculate_grading_roi(
    raw_cost: float,
    psa10_comp: float,
    psa9_comp: float,
    grading_fee: float = 39.99,
    shipping_supplies: float = 5.00,
    gem_probability: float = 0.45,
) -> GradingROIResult:
    """Calculates expected value (EV) and PSA 9 salvage cushion for a raw-to-grade candidate."""
    all_in_grade_cost = grading_fee + shipping_supplies
    gem_net_gain = psa10_comp - raw_cost - all_in_grade_cost
    psa9_salvage_net = psa9_comp - raw_cost - all_in_grade_cost

    expected_post_grade = (gem_probability * psa10_comp) + ((1 - gem_probability) * psa9_comp)
    expected_net_profit = expected_post_grade - raw_cost - all_in_grade_cost
    roi_pct = (expected_net_profit / max(all_in_grade_cost, 1.0)) * 100

    if expected_net_profit > 50 and psa9_salvage_net >= -25:
        verdict = "Strong Submit — High upside with protected PSA 9 floor"
    elif expected_net_profit > 0:
        verdict = "Conditional Submit — Worth grading only if centering & surface are clean"
    else:
        verdict = "Skip Grading — Sell raw; grading fee outweighs expected upside"

    return GradingROIResult(
        gem_net_gain=round(gem_net_gain, 2),
        psa9_salvage_net=round(psa9_salvage_net, 2),
        expected_net_profit=round(expected_net_profit, 2),
        roi_on_grading_fee_pct=round(roi_pct, 1),
        verdict=verdict,
    )
