from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SellRecommendation:
    primary_channel: str
    headline: str
    rationale: str
    net_payouts: Dict[str, float]
    warning_flag: Optional[str] = None


def evaluate_best_sell_channel(
    market_comp: float,
    psa_offer: Optional[float] = None,
    liquidity: str = "Medium",
    goal: str = "Balanced",
    is_offseason: bool = False,
    ebay_fee_rate: float = 0.1325,
    shipping_cost: float = 5.50,
) -> SellRecommendation:
    """
    Calculates net payouts across selling venues and recommends the optimal
    exit or hold strategy for a graded card in Statsline.
    """
    if market_comp <= 0:
        raise ValueError("Market comp must be greater than $0.")

    ebay_net = max(0.0, (market_comp * (1 - ebay_fee_rate)) - shipping_cost)

    if market_comp < 50:
        consign_rate = 0.25
    elif market_comp < 250:
        consign_rate = 0.18
    else:
        consign_rate = 0.13
    consign_net = max(0.0, market_comp * (1 - consign_rate))

    net_payouts = {
        "eBay Fixed Price (DIY)": round(ebay_net, 2),
        "eBay Auction (7-Day)": round(ebay_net * 0.94, 2),
        "Consignment / COMC": round(consign_net, 2),
    }

    offer_pct = 0.0
    if psa_offer and psa_offer > 0:
        net_payouts["PSA Partner Offer"] = round(psa_offer, 2)
        offer_pct = (psa_offer / market_comp) * 100

    if goal == "Long-Term Hold" or (is_offseason and goal != "Fast Cash"):
        reason = (
            "Card is currently in an off-season demand dip—holding in a secure vault "
            "avoids selling into weak comps."
            if is_offseason
            else "Flagged as a long-term core hold; keep off home premises in PSA Vault, Fanatics, or an insured off-site safe."
        )
        return SellRecommendation(
            primary_channel="Vault & Hold",
            headline="Hold in Secure Vault (Do Not Sell Now)",
            rationale=reason,
            net_payouts=net_payouts,
            warning_flag="Avoid listing during off-season slumps unless you need immediate cash.",
        )

    if psa_offer and offer_pct >= 88.0:
        return SellRecommendation(
            primary_channel="PSA Partner Offer",
            headline=f"Accept PSA Partner Offer (${psa_offer:,.2f} • {offer_pct:.1f}% of Comp)",
            rationale=(
                f"At {offer_pct:.1f}% of market value with $0 shipping and zero return risk, "
                f"this beats or matches your estimated eBay net (${ebay_net:,.2f}) instantly."
            ),
            net_payouts=net_payouts,
        )

    if psa_offer and offer_pct >= 80.0 and (goal in ["Fast Cash", "Zero Hassle"] or market_comp < 150):
        return SellRecommendation(
            primary_channel="PSA Partner Offer",
            headline=f"Accept PSA Partner Offer (${psa_offer:,.2f} • {offer_pct:.1f}% of Comp)",
            rationale=(
                f"Saves packing, shipping, and eBay listing time while netting within "
                f"${max(0.0, ebay_net - psa_offer):,.2f} of a DIY eBay sale."
            ),
            net_payouts=net_payouts,
        )

    if goal == "Zero Hassle" or (market_comp < 75 and goal != "Max Profit"):
        return SellRecommendation(
            primary_channel="Consignment / COMC",
            headline=f"Send to Consignment / COMC (~${consign_net:,.2f} Est. Net)",
            rationale=(
                "Outsourcing scanning, listing, and shipping makes sense when time-per-slab "
                "outweighs the small fee difference over DIY eBay."
            ),
            net_payouts=net_payouts,
            warning_flag="Check consignment payout minimums and processing turnaround times.",
        )

    if goal == "Fast Cash":
        if liquidity == "High":
            return SellRecommendation(
                primary_channel="eBay Auction (7-Day)",
                headline=f"Run a 7-Day Auction (~${net_payouts['eBay Auction (7-Day)']:,.2f} Est. Net)",
                rationale=(
                    "High collector liquidity means two or more active bidders are likely to compete, "
                    "forcing a clean sale within 7 days."
                ),
                net_payouts=net_payouts,
                warning_flag="End auction on Sunday evening (7–9 PM EST) for peak bidder traffic.",
            )
        return SellRecommendation(
            primary_channel="eBay Fixed Price (Best Offer)",
            headline=f"List Fixed Price + Best Offer (~${ebay_net:,.2f} Est. Net)",
            rationale=(
                "Lower liquidity means an auction risks a single-bidder bargain; Fixed Price "
                "protects your floor while Best Offer lets you accept a quick fair bid."
            ),
            net_payouts=net_payouts,
            warning_flag="Avoid 7-day auctions on niche/low-pop slabs without 2+ guaranteed bidders.",
        )

    return SellRecommendation(
        primary_channel="eBay Fixed Price (Buy It Now)",
        headline=f"List Fixed Price Buy It Now (~${ebay_net:,.2f} Est. Net)",
        rationale=(
            "Gives you strict control over final price and maximizes net take-home when you aren't forced to sell overnight."
        ),
        net_payouts=net_payouts,
        warning_flag=(
            f"PSA Offer (${psa_offer:,.2f}, {offer_pct:.1f}%) is too low—hold firm on Fixed Price."
            if psa_offer and offer_pct < 75.0
            else None
        ),
    )
