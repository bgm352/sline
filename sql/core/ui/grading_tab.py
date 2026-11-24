import streamlit as st
from core.centering import estimate_borders_opencv, measure_centering_from_borders
from core.grading_roi import calculate_grading_roi


def render_grading_tab():
    st.subheader("🔍 Pre-Grading Centering & ROI Calculator")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Border Centering Check**")
        uploaded = st.file_uploader(
            "Upload front photo of raw card (optional)",
            type=["png", "jpg", "jpeg"],
        )
        default_l, default_r, default_t, default_b = (50.0, 50.0, 50.0, 50.0)
        if uploaded:
            st.image(uploaded, width=220)
            default_l, default_r, default_t, default_b = estimate_borders_opencv(
                uploaded.getvalue()
            )

        l_px = st.number_input("Left Border (px)", min_value=1.0, value=float(round(default_l, 1)))
        r_px = st.number_input("Right Border (px)", min_value=1.0, value=float(round(default_r, 1)))
        t_px = st.number_input("Top Border (px)", min_value=1.0, value=float(round(default_t, 1)))
        b_px = st.number_input("Bottom Border (px)", min_value=1.0, value=float(round(default_b, 1)))

        c_res = measure_centering_from_borders(l_px, r_px, t_px, b_px)
        st.info(
            f"**L/R:** {c_res.left_right_ratio[0]} / {c_res.left_right_ratio[1]}  |  "
            f"**T/B:** {c_res.top_bottom_ratio[0]} / {c_res.top_bottom_ratio[1]}\n\n"
            f"**Status:** {c_res.verdict}"
        )

    with col2:
        st.markdown("**2. Raw-to-Graded Profit Math**")
        raw_cost = st.number_input("Raw Value / Purchase Price ($)", min_value=0.0, value=295.0, step=5.0)
        psa10_comp = st.number_input("PSA 10 Comp ($)", min_value=1.0, value=1225.0, step=10.0)
        psa9_comp = st.number_input("PSA 9 Salvage Comp ($)", min_value=1.0, value=340.0, step=10.0)
        fee = st.number_input("Grading Fee ($)", min_value=1.0, value=39.99, step=1.0)
        gem_prob = st.slider("Estimated PSA 10 Probability (%)", 10, 90, 40) / 100.0

        roi = calculate_grading_roi(
            raw_cost, psa10_comp, psa9_comp, grading_fee=fee, gem_probability=gem_prob
        )
        st.success(f"**Verdict:** {roi.verdict}")
        m1, m2, m3 = st.columns(3)
        m1.metric("PSA 10 Net Gain", f"${roi.gem_net_gain:,.2f}")
        m2.metric("PSA 9 Net", f"${roi.psa9_salvage_net:,.2f}")
        m3.metric("Expected EV", f"${roi.expected_net_profit:,.2f}")
