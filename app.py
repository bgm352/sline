from dotenv import load_dotenv
import streamlit as st

from ui.vault_tab import render_vault_tab
from ui.grading_tab import render_grading_tab
from ui.sell_tab import render_sell_optimizer

load_dotenv()

st.set_page_config(
    page_title="Statsline — Card Vault, Grading & Sell Engine",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Statsline")
st.caption(
    "Track what cards you own, check whether a card's border is evenly centered, "
    "calculate whether paying to grade is worth the cost, and pick the smartest way to sell."
)

tab_vault, tab_grade, tab_sell = st.tabs(
    ["🗂️ Vault", "🔍 Pre-Grade & ROI", "💰 Best Way to Sell"]
)

with tab_vault:
    render_vault_tab()

with tab_grade:
    render_grading_tab()

with tab_sell:
    render_sell_optimizer()
