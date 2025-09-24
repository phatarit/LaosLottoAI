# app.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter

st.set_page_config(
    page_title="Lao Lotto: ทำนายจาก 5 งวด",
    page_icon="🇱🇦",
    layout="centered"
)

# ----------------- STYLE -----------------
st.markdown("""
<style>
:root{
  --blue:#1f57c3;
  --red:#e0252a;
}
.stApp { background:#f7f9ff; }
.block-container{ max-width:820px; }
.title {
  color: var(--blue); font-weight:800; font-size: 1.8rem;
  margin: 0.5rem 0 1rem 0; text-align:center;
}
.card {
  background:#ffffff; border:3px solid var(--blue); border-radius:16px;
  padding:14px 16px; margin:10px 0 16px 0; box-shadow: 0 6px 18px rgba(0,0,0,0.07);
}
.tag {
  display:inline-block; background:var(--blue); color:#fff;
  padding:4px 12px; border-radius:999px; font-weight:700; letter-spacing:0.5px;
}
.num-xl { color:var(--red); font-weight:900; font-size:3.2rem; line-height:1; }
.num-lg { color:var(--red); font-weight:900; font-size:2.4rem; line-height:1; }
.num-md { color:var(--red); font-weight:900; font-size:2.1rem; line-height:1; }
.num-sm { color:var(--red); font-weight:900; font-size:1.9rem; line-height
