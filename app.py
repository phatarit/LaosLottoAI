# app_v7.2_hybrid.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict
import math
import numpy as np

st.set_page_config(page_title="Lao Lotto V.7.2", page_icon="🎯", layout="centered")

# ----------------- STYLE -----------------
st.markdown("""
<style>
:root{ --blue:#1f57c3; --red:#e0252a; --ink:#0f172a; }
.stApp { background:#f7f9ff; }
.block-container{ max-width:1024px; }
.title { color: var(--blue); font-weight:900; font-size: 2.2rem; line-height:1.1; }
.subtitle { color:#1f2937; margin-top:6px; font-size:1.0rem; }
.card {
  background:#ffffff; border:3px solid var(--blue); border-radius:18px;
  padding:18px 20px; margin:14px 0 18px 0; box-shadow: 0 8px 22px rgba(0,0,0,0.08);
}
.heading { font-weight:900; font-size:1.25rem; color:#0f172a; margin:8px 0 12px; }
.num-xl { color:var(--red); font-weight:900; font-size:4.2rem; display:flex; gap:40px; align-items:baseline; flex-wrap:wrap; justify-content:center;}
.num-xl .label{ font-size:1.4rem; font-weight:800; color:#0f172a; background:#eef2ff; border:2px solid #c7d2fe; border-radius:12px; padding:6px 14px; }
.num-xl .digit{ font-size:4.8rem; font-weight:900; color:var(--red); margin-left:12px; }
.num-lg { font-weight:900; font-size:2.6rem; line-height:1.25; }
.num-md { font-weight:900; font-size:2.2rem; line-height:1.25; }
.num-sm { font-weight:900; font-size:2.0rem; }
.tag { display:inline-block; padding:4px 12px; border-radius:12px; background:#eef2ff; border:1px solid #c7d2fe; color:#0f172a; font-weight:700; font-size:1.0rem; margin-left:12px;}
.badge { display:inline-flex; align-items:baseline; gap:10px; padding:6px 12px; border:2px solid var(--red); border-radius:14px; margin:6px 10px 0 0; }
.perc { font-size:1.0rem; color:#0f172a; background:#fff; border:1px dashed #c7d2fe; padding:2px 8px; border-radius:10px; }
.footer { text-align:center; margin: 18px 0 8px 0; color:#475569; font-weight:700; }
.digit-red { color: var(--red) !important; font-weight:900; }
.tip { display:inline-block; margin-top:6px; padding:6px 10px; background:#fff7ed; border:1px solid #fdba74; color:#7c2d12; border-radius:10px; font-weight:700; }
.small { color:#475569; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.7.2 — Hybrid & Calibrated</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Hybrid pool (conditional odds/PMI) · Isotonic calibration · Anti-bias penalty · Custom 4-digit rule</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "กรุณาวาง 'งวดล่าสุด 10 งวด' (4 หลัก/บรรทัด) เช่น 9767\\n5319\\n1961 ..."
st.markdown("<span class='tip'>คำชี้แจง: กรุณาลงงวดล่าสุด 10 งวด (ระบบจะใช้เฉพาะ 10 งวดท้ายสุด)</span>", unsafe_allow_html=True)
raw = st.text_area("ผลย้อนหลัง (ใช้เฉพาะ 10 งวดล่าสุดจากรายการที่วาง)", height=260, placeholder=ph)

# อ่านข้อมูล
all_draws = [s.strip() for s in raw.splitlines() if s.strip().isdigit() and len(s.strip())==4]
st.write(f"อ่านข้อมูลได้ทั้งหมด **{len(all_draws)}** งวด")
if len(all_draws) < 10:
    st.info("กรุณาวางอย่างน้อย 10 งวดล่าสุด (ระบบจะใช้เฉพาะ 10 งวดท้ายสุดอัตโนมัติ).", icon="ℹ️")
    st.stop()

# ใช้เฉพาะ 10 งวดล่าสุด
draws = all_draws[-10:]
st.write("กำลังวิเคราะห์ **10 งวดล่าสุด** จากรายการที่วางมา ✅")
N = len(draws)
recent5 = draws[-5:] if N >= 5 else draws

# ----------------- HELPERS -----------------
def pct(x): 
    try:
        return f"{x*100:.1f}%"
    except:
        return "—"

def safe_div(a,b,eps=1e-9): return a/ b if b>0 else 0.0
def normalize_scores(sc):
    v=list(sc.values()); lo,hi=min(v),max(v)
    return {k:(v_ - lo)/(hi-lo) if hi>lo else 1.0 for k,v_ in sc.items()}

def logit(p,eps=1e-6): 
    p = min(max(p,eps),1-eps)
    return math.log(p/(1-p))

def sigmoid(x): 
    try:
        return 1.0/(1.0+math.exp(-x))
    except OverflowError:
        return 0.0 if x<-50 else 1.0

def quantile_bins(xs, qs):
    # return (bin_edges, bin_idx_of_each_x)
    xs_np=np.array(xs)
    edges=np.quantile(xs_np, qs)
    # ensure strictly in
