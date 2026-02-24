import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Gerlach (2018) - 4 Personality Types",
    page_icon="🧭",
    layout="wide",
)

st.title("Gerlach (2018): Four Personality Types")

st.markdown(
    "This page summarizes the four robust personality types reported in Gerlach et al. (2018), "
    "based on clustering Big Five (N/E/O/A/C) trait profiles across large datasets."
)

st.markdown("---")

with st.sidebar:
    st.markdown("## View Mode")
    view_mode = st.radio(
        "Choose how to display the Big Five profiles:",
        [
            "Option C — Strict (text-only)",
            "Option B — Complete 5D (fill missing)",
        ],
        index=0,
    )

TYPE_DEFINITIONS = [
    {
        "key": "average",
        "name": "Average",
        "tagline": "Average scores across all five traits.",
        "description": (
            "Characterized by approximately average (near-zero z-score) values on Neuroticism, "
            "Extraversion, Openness, Agreeableness, and Conscientiousness."
        ),
        "traits": {"N": "avg", "E": "avg", "O": "avg", "A": "avg", "C": "avg"},
    },
    {
        "key": "role_model",
        "name": "Role model",
        "tagline": "Low Neuroticism, high on the other four traits.",
        "description": (
            "Described as socially desirable: low Neuroticism and high Extraversion, Openness, "
            "Agreeableness, and Conscientiousness. Identified with the classic ‘resilient’ type."
        ),
        "traits": {"N": "low", "E": "high", "O": "high", "A": "high", "C": "high"},
    },
    {
        "key": "self_centred",
        "name": "Self-centred",
        "tagline": "Low Openness, Agreeableness, and Conscientiousness.",
        "description": (
            "One of the less socially desirable clusters. In the article text, it is marked by low "
            "scores on Openness, Agreeableness, and Conscientiousness (O/A/C)."
        ),
        "traits": {"N": "—", "E": "—", "O": "low", "A": "low", "C": "low"},
    },
    {
        "key": "reserved",
        "name": "Reserved",
        "tagline": "Low Neuroticism and low Openness.",
        "description": (
            "Another less socially desirable cluster. In the article text, it shows low scores on "
            "Neuroticism and Openness (N/O)."
        ),
        "traits": {"N": "low", "E": "—", "O": "low", "A": "—", "C": "—"},
    },
]

TRAIT_FULL = {
    "N": "Neuroticism",
    "E": "Extraversion",
    "O": "Openness",
    "A": "Agreeableness",
    "C": "Conscientiousness",
}

LABEL_STYLE = {
    "high": "High",
    "low": "Low",
    "avg": "Average",
    "—": "Not specified in text excerpt",
}

COLOR = {
    "high": "#1b9e77",
    "low": "#d95f02",
    "avg": "#7570b3",
    "—": "#666666",
}


def render_trait_badges(traits: dict) -> None:
    cols = st.columns(5)
    for i, t in enumerate(["N", "E", "O", "A", "C"]):
        val = traits.get(t, "—")
        label = LABEL_STYLE.get(val, str(val))
        color = COLOR.get(val, "#666666")
        with cols[i]:
            st.markdown(
                f"<div style='border:1px solid #ddd;border-radius:10px;padding:10px;'>"
                f"<div style='font-size:0.85rem;color:#666;margin-bottom:6px;'><b>{t}</b> {TRAIT_FULL[t]}</div>"
                f"<div style='font-size:1.05rem;color:{color};'><b>{label}</b></div>"
                f"</div>",
                unsafe_allow_html=True,
            )


def get_effective_traits(tdef: dict) -> dict:
    """Return traits depending on view mode.

    - Option C: keep the original text-only trait markings (unknown stays as '—').
    - Option B: allow user to fill unknown traits (per-type) in the sidebar.
    """
    base = dict(tdef["traits"])
    if view_mode != "Option B — Complete 5D (fill missing)":
        return base

    # Only allow editing for traits that are unknown in the text-only profile.
    missing = [k for k, v in base.items() if v == "—"]
    if not missing:
        return base

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Fill Missing Traits")
    st.sidebar.caption(
        "This mode lets you complete the 5D profile without guessing in code. "
        "Set values based on the paper’s figures/tables."
    )

    options = ["avg", "high", "low"]
    for trait_key in missing:
        state_key = f"fill_{tdef['key']}_{trait_key}"
        if state_key not in st.session_state:
            st.session_state[state_key] = "avg"
        st.session_state[state_key] = st.sidebar.selectbox(
            f"{tdef['name']} — {trait_key} ({TRAIT_FULL[trait_key]})",
            options,
            index=options.index(st.session_state[state_key]),
        )
        base[trait_key] = st.session_state[state_key]

    return base


st.subheader("Type Cards")

cols = st.columns(2)
for idx, tdef in enumerate(TYPE_DEFINITIONS):
    with cols[idx % 2]:
        st.markdown(
            f"<div style='border:2px solid #e6e6e6;border-radius:14px;padding:16px;margin-bottom:14px;background:#fafafa;'>"
            f"<div style='font-size:1.35rem;'><b>{tdef['name']}</b></div>"
            f"<div style='color:#555;margin-top:4px;margin-bottom:10px;'><i>{tdef['tagline']}</i></div>"
            f"<div style='color:#333;margin-bottom:12px;'>{tdef['description']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        effective_traits = get_effective_traits(tdef)
        render_trait_badges(effective_traits)
        st.markdown("&nbsp;", unsafe_allow_html=True)

st.markdown("---")

st.subheader("Comparison Table (Big Five profile)")

table_rows = []
for tdef in TYPE_DEFINITIONS:
    row = {"Type": tdef["name"]}
    effective_traits = get_effective_traits(tdef)
    for t in ["N", "E", "O", "A", "C"]:
        val = effective_traits.get(t, "—")
        row[t] = LABEL_STYLE.get(val, val)
    table_rows.append(row)

df = pd.DataFrame(table_rows, columns=["Type", "N", "E", "O", "A", "C"])
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader("Source")
st.markdown(
    "Gerlach, M., Farb, B., Revelle, W., & Nunes Amaral, L. A. (2018). "
    "A robust data-driven approach identifies four personality types across four large data sets. "
    "*Nature Human Behaviour*."
)

st.caption(
    "Note: Some trait directions for the Self-centred and Reserved types are presented here exactly as described in the article text. "
    "For the complete 5-trait z-score profiles, refer to the paper’s figures/tables."
)
