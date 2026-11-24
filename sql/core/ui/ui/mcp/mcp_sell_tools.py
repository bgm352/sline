import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

# Ensure repo root is on sys.path when running directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field
from supabase import Client, create_client

from core.sell_recommender import evaluate_best_sell_channel

load_dotenv()
mcp = FastMCP(name="Statsline Vault Advisor")


def _get_supabase_client() -> Client:
    """Initializes a Supabase client from environment variables."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or Supabase API key environment variables.")
    return create_client(url, key)


@mcp.tool(
    name="recommend_card_sell_venue",
    description=(
        "Evaluates the best selling or holding venue (PSA Partner Offer, eBay Fixed Price, "
        "7-Day eBay Auction, Consignment/COMC, or Vault & Hold) for a sports or TCG card "
        "and calculates estimated net payouts after fees and shipping."
    ),
)
def recommend_card_sell_venue(
    market_comp: float = Field(gt=0, description="Current market comp value in USD."),
    psa_offer: Optional[float] = Field(
        default=None,
        ge=0,
        description="Optional instant PSA Partner/Vault offer amount in USD.",
    ),
    liquidity: Literal["High", "Medium", "Niche"] = Field(
        default="Medium",
        description="Market liquidity and bidder depth for the card.",
    ),
    goal: Literal["Balanced", "Fast Cash", "Max Profit", "Zero Hassle", "Long-Term Hold"] = Field(
        default="Balanced",
        description="Seller objective for speed, net return, low effort, or holding.",
    ),
    is_offseason: bool = Field(
        default=False,
        description="True if the card's sport is currently in its off-season.",
    ),
    ebay_fee_rate: float = Field(
        default=0.1325,
        ge=0,
        lt=1,
        description="Estimated eBay fee decimal rate (default 0.1325 = 13.25%).",
    ),
    shipping_cost: float = Field(
        default=5.50,
        ge=0,
        description="Estimated shipping and packing cost in USD for a DIY sale.",
    ),
) -> Dict[str, Any]:
    """Wraps evaluate_best_sell_channel for single-card AI tool calls."""
    rec = evaluate_best_sell_channel(
        market_comp=market_comp,
        psa_offer=psa_offer if (psa_offer is not None and psa_offer > 0) else None,
        liquidity=liquidity,
        goal=goal,
        is_offseason=is_offseason,
        ebay_fee_rate=ebay_fee_rate,
        shipping_cost=shipping_cost,
    )
    return asdict(rec)


@mcp.tool(
    name="recommend_vault_sell_plan",
    description=(
        "Queries cards from the Statsline vault table in Supabase and returns "
        "selling or holding recommendations and net payout estimates for matching slabs."
    ),
)
def recommend_vault_sell_plan(
    card_query: Optional[str] = Field(
        default=None,
        description="Optional player, set, or card name filter (case-insensitive substring).",
    ),
    goal: Literal["Balanced", "Fast Cash", "Max Profit", "Zero Hassle", "Long-Term Hold"] = Field(
        default="Balanced",
        description="Override goal applied across queried vault cards.",
    ),
    is_offseason: bool = Field(
        default=False,
        description="True if evaluating during an off-season demand window.",
    ),
    table_name: str = Field(
        default="vault_cards",
        description="Supabase table name storing vault cards.",
    ),
    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum number of vault cards to evaluate.",
    ),
) -> List[Dict[str, Any]]:
    """Fetches vault cards from Supabase and scores each card's best exit/hold channel."""
    supabase = _get_supabase_client()
    query = supabase.table(table_name).select("*").limit(limit)
    if card_query:
        query = query.ilike("card_name", f"%{card_query}%")

    rows = query.execute().data or []
    results: List[Dict[str, Any]] = []

    for row in rows:
        comp = float(row.get("market_comp") or row.get("estimated_value") or 0.0)
        if comp <= 0:
            continue

        raw_offer = row.get("psa_offer")
        psa_offer = float(raw_offer) if raw_offer is not None and float(raw_offer) > 0 else None
        card_goal = goal if goal != "Balanced" else (row.get("default_goal") or "Balanced")
        card_liquidity = row.get("liquidity") or "Medium"

        rec = evaluate_best_sell_channel(
            market_comp=comp,
            psa_offer=psa_offer,
            liquidity=card_liquidity,
            goal=card_goal,
            is_offseason=is_offseason,
        )

        results.append(
            {
                "id": row.get("id"),
                "card_name": row.get("card_name", "Unknown Card"),
                "grade": row.get("grade"),
                "market_comp": comp,
                "recommendation": asdict(rec),
            }
        )

    return results


if __name__ == "__main__":
    mcp.run()
