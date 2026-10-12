"""Suspended deployment notice.

This app was previously served from the `korean` branch. The Korean study now
runs from the `main` branch (APP_LANG=ko), so this URL is retired.
"""
import streamlit as st

st.set_page_config(page_title="URL Suspended", page_icon="🚫")

st.title("This URL has been suspended")
st.write("This URL has been suspended and is no longer within the project scope.")
st.write("이 URL은 사용이 중지되었으며 더 이상 본 연구 프로젝트의 범위에 포함되지 않습니다.")
st.write("Please use the link provided to you by the research team.")
