import pandas as pd
import streamlit as st
from core.sell_recommender import evaluate_best_sell_channel


def render_sell_optimizer():
    st.subheader("💰 Best Way to Sell — Exit Strategy Engine")
    st.caption("Compare instant PSA offers, DIY eBay net payouts, consignment, and vault holds.")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Card Name & Grade",
            value="2023 Pokémon 151 Charizard ex #199 SIR — PSA 10",
        )
        market_comp = st.number_input(
            "Current Market Comp ($)", min_value=1.0, value=1225.0, step=5.0
        )
        psa_offer = st.number_input(
            "PSA Partner Offer ($ — 0 if none)", min_value=0.0, value=1080.0, step=5.0
        )

    with col2:
        liquidity = st.selectbox("Market Liquidity", ["High", "Medium", "Niche"], index=0)
        goal = st.selectbox(
            "Primary Goal",
            ["Balanced", "Fast Cash", "Max Profit", "Zero Hassle", "Long-Term Hold"],
            index=0,
        )
        is_offseason = st.checkbox("Currently in Sport Off-Season?", value=False)

    rec = evaluate_best_sell_channel(
        market_comp=market_comp,
        psa_offer=psa_offer if psa_offer > 0 else None,
        liquidity=liquidity,
        goal=goal,
        is_offseason=is_offseason,
    )

    st.success(f"**Recommended Route:** {rec.headline}")
    st.write(rec.rationale)
    if rec.warning_flag:
        st.warning(f"⚠️ **Tip:** {rec.warning_flag}")

    df = pd.DataFrame(
        [
            {
                "Channel": channel,
                "Est. Net Payout": f"${amt:,.2f}",
                "% of Comp": f"{(amt / market_comp) * 100:.1f}%",
            }
            for channel, amt in rec.net_payouts.items()
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
