
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Hesap Kurdu",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

html_path = Path(__file__).parent / "index.html"

if not html_path.exists():
    st.error("index.html dosyası bulunamadı. Dosyayı app.py ile aynı klasöre yükleyin.")
    st.stop()

html = html_path.read_text(encoding="utf-8")

components.html(
    html,
    height=1200,
    scrolling=True,
)
