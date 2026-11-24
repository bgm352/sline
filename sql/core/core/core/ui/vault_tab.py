import os
import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import Client, create_client


def _get_secret(key: str) -> str | None:
    """Reads a secret from st.secrets first, falling back to environment variables."""
    try:
        if key in st.secrets:
            val = st.secrets[key]
            if val:
                return str(val)
    except StreamlitSecretNotFoundError:
        pass
    except Exception:
        pass

    env_val = os.getenv(key)
    return env_val if env_val else None


def _get_supabase() -> Client | None:
    url = _get_secret("SUPABASE_URL")
    key = _get_secret("SUPABASE_ANON_KEY")
    if url and key:
        return create_client(url, key)
    return None


def render_vault_tab():
    st.subheader("🗂️ Card Vault & Portfolio Tracker")
    supabase = _get_supabase()

    if "local_vault" not in st.session_state:
        st.session_state.local_vault = [
            {
                "card_name": "1952 Bowman Mickey Mantle #101",
                "grade": "PSA 3",
                "cost_basis": 3500.0,
                "market_comp": 6565.0,
                "default_goal": "Long-Term Hold",
            },
            {
                "card_name": "1948 Bowman Yogi Berra #6",
                "grade": "PSA 4",
                "cost_basis": 850.0,
                "market_comp": 1533.0,
                "default_goal": "Long-Term Hold",
            },
        ]

    if supabase:
        rows = (
            supabase.table("vault_cards")
            .select("*")
            .order("market_comp", desc=True)
            .execute()
            .data
            or []
        )
    else:
        st.info(
            "Running in local demo mode (add SUPABASE_URL and SUPABASE_ANON_KEY to "
            ".streamlit/secrets.toml, Streamlit Cloud Secrets, or .env to persist)."
        )
        rows = st.session_state.local_vault

    if rows:
        df = pd.DataFrame(rows)
        total_value = df["market_comp"].sum()
        total_cost = df["cost_basis"].fillna(0).sum() if "cost_basis" in df else 0.0
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Cards", len(df))
        c2.metric("Est. Portfolio Value", f"${total_value:,.2f}")
        c3.metric("Tracked Cost Basis", f"${total_cost:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("➕ Add Card to Vault"):
        with st.form("add_card_form"):
            name = st.text_input("Card Name")
            grade = st.text_input("Grade", value="Raw")
            cost = st.number_input("Cost Basis ($)", min_value=0.0, step=5.0)
            comp = st.number_input("Market Comp ($)", min_value=1.0, step=5.0)
            goal = st.selectbox(
                "Default Goal",
                ["Balanced", "Fast Cash", "Max Profit", "Zero Hassle", "Long-Term Hold"],
            )
            submitted = st.form_submit_button("Save Card")

            if submitted and name:
                record = {
                    "card_name": name,
                    "grade": grade,
                    "cost_basis": cost,
                    "market_comp": comp,
                    "default_goal": goal,
                }
                if supabase:
                    supabase.table("vault_cards").insert(record).execute()
                else:
                    st.session_state.local_vault.append(record)
                st.success(f"Added {name} to vault.")
                st.rerun()
