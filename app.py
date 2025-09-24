# app.py
# -*- coding: utf-8 -*-
import random
import re
from collections import Counter
import streamlit as st

# ───────────── Page config ─────────────
st.set_page_config(
    page_title="🇱🇦 Lao Lotto — วิเคราะห์ & ทำนาย (4 หลัก)",
    page_icon="🇱🇦",
    layout="centered",
)

# ───────────── Theme (ขาว/แดง/น้ำเงิน) ─────────────
st.markdown("""
<style>
/* พื้นหลังขาว ตัวอักษรหลักสีเข้ม */
.stApp { background:#ffffff; color:#111; }
.block-container { max-width: 880px; }

/* หัวเรื่องสีน้ำเงิน */
h1, h2, h3, .title-blue { color:#0b48c2 !important; }

/* กล่องผลลัพธ์: ขอบน้ำเงิน พื้นขาว ตัวเลขแดง */
.result-box {
  background:#fff; border:3px solid #0b48c2; border-radius:14px;
  padding:14px 16px; margin:10px 0;
}
.big-red   { color:#d60b24; font-weight:800; font-size:3rem; line-height:1.0; }
.mid-red   { color:#d60b24; font-weight:800; font-size:2.0rem; }
.small-red { color:#d60b24; font-weight:800; font-size:1.6rem; }

/* ปุ่ม/อินพุต */
textarea, .stTextArea textarea {
  background:#fff; border:2px solid #0b48c2; color:#111;
}
.stButton>button {
  background:#0b48c2; color:#fff; font-weight:600; border:none;
  border-radius:10px; padding:0.55rem 1.0rem;
}
.stButton>button:hover { filter:brightness(1.05); }
.tip { font-size:0.9rem; color:#444; }
.sep { border-color:#dfe6ff; }
</style>
""", unsafe_allow_html=True)

# ───────────── Title ─────────────
st.markdown(
    "<h1 class='title-blue'>🇱🇦 Lao Lotto — วิเคราะห์ & ทำนาย (4 หลัก)</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='tip'>วางเลข 4 หลัก ทีละบรรทัด (อย่างน้อย 10 งวด) — "
    "ระบบจะล้างอักขระอื่น ๆ และ<strong>ถ้าเกิน 4 หลักจะใช้ 4 หลักท้ายสุด</strong></div>",
    unsafe_allow_html=True,
)

# ───────────── Input ─────────────
default_text = ""
raw = st.text_area(
    "วางเลข 4 หลัก",
    value=default_text,
    height=220,
    placeholder="เช่น 0543\n0862\n9252\n… (อย่างน้อย 10 งวด)",
)

# ล้างข้อมูล: เอาเฉพาะตัวเลข, ถ้ายาวกว่า 4 ให้ใช้ 4 ตัวท้าย, ถ้าน้อยกว่า 4 ทิ้ง
def clean_to_last4(line: str) -> str | None:
    digits = re.sub(r"\D", "", line)
    if len(digits) < 4:
        return None
    return digits[-4:]

lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
draws4 = []
for ln in lines:
    last4 = clean_to_last4(ln)
    if last4:
        draws4.append(last4)

st.write(f"📥 โหลดข้อมูลที่ผ่านการล้างรูปแบบ: **{len(draws4)}** งวด")

if len(draws4) < 10:
    st.warning("ต้องมีอย่างน้อย **10 งวด**")
    st.stop()

# ───────────── Helpers ─────────────
def digits_in(s: str):
    return list(s)  # คืน ['9','2','5','2']

def hot_digit_last_8(draws: list[str]) -> str:
    last8 = draws[-8:]
    cnt = Counter()
    for d in last8:
        cnt.update(digits_in(d))
    if not cnt:
        return "0"
    # ถ้าเสมอ เลือกตัวที่ค่าจริงต่ำสุด (เสถียร)
    top = max(cnt.items(), key=lambda x: (x[1], -int(x[0])))
    return top[0]

def partners_from_last3(draws: list[str]) -> list[str]:
    last3 = draws[-3:]
    seen = []
    for d in last3:
        for ch in digits_in(d):
            if ch not in seen:
                seen.append(ch)
    return seen  # รักษาลำดับที่พบ

def missing_digit_in_last5(draws: list[str]) -> str:
    last5 = draws[-5:]
    seen = set()
    for d in last5:
        seen |= set(digits_in(d))
    # ถ้ามีเลขหายไป เลือกตัวที่น้อยสุด, ถ้าไม่มีให้เลือกตัวที่พบน้อยสุดใน 5 งวด
    for z in [str(i) for i in range(10)]:
        if z not in seen:
            return z
    cnt = Counter()
    for d in last5:
        cnt.update(digits_in(d))
    minc = min(cnt.values())
    cands = [z for z, c in cnt.items() if c == minc]
    return sorted(cands, key=lambda x: int(x))[0]

# ───────────── Step 1: เลขเดี่ยว (เกิดถี่สุด) 8 งวดล่าสุด ─────────────
hot = hot_digit_last_8(draws4)

st.markdown("<div class='result-box'><div>1) เลขเดี่ยว (เกิดถี่สุด) — 8 งวดล่าสุด</div>"
            f"<div class='big-red'>{hot}</div></div>", unsafe_allow_html=True)

# ───────────── Step 2: จับคู่เลขสองตัวจากเลขงวดก่อนหน้า 3 งวด ─────────────
special_order = ['4','5','6','2','1','0']  # ลำดับเลขพิเศษ
last3_partners = partners_from_last3(draws4)

# จัดลำดับ partner: เอาเลขพิเศษที่ปรากฏใน 3 งวดล่าสุดก่อน (ตามลำดับ special_order)
ordered = []
for s in special_order:
    if s in last3_partners and s not in ordered and s != hot:
        ordered.append(s)
# ตามด้วยเลขอื่น ๆ จาก 3 งวดล่าสุด
for p in last3_partners:
    if p != hot and p not in ordered:
        ordered.append(p)
# ถ้ายังไม่ครบ เติมจากเลขพิเศษที่ไม่อยู่ และเลข 0–9
for s in special_order:
    if s != hot and s not in ordered:
        ordered.append(s)
for d in [str(i) for i in range(10)]:
    if d != hot and d not in ordered:
        ordered.append(d)

pairs_all = [hot + p for p in ordered]
pairs_top5 = pairs_all[:5]

st.markdown("<div class='result-box'><div>2) เลขสองตัว (จากเลขเดี่ยว × เลข 3 งวดล่าสุด, เน้น 4-5-6-2-1-0 ก่อน)</div>"
            f"<div class='mid-red'>{', '.join(pairs_top5)}</div></div>", unsafe_allow_html=True)

# ───────────── Step 3: เลขสามตัว = ใส่เลขที่ “หายไป” จาก 5 งวดล่าสุด ไว้ด้านหน้า ─────────────
missing_prefix = missing_digit_in_last5(draws4)
triplets = [missing_prefix + p for p in pairs_top5]

st.markdown("<div class='result-box'><div>3) เลขสามตัว — ใส่เลขที่หายไปจาก 5 งวดล่าสุดไว้ด้านหน้า</div>"
            f"<div class='mid-red'>{', '.join(triplets)}</div></div>", unsafe_allow_html=True)

# ───────────── Step 4: เลขสี่ตัว 1 ชุด (สุ่มเลือกหนึ่งจากข้อ 3) แล้วเติมหลักพันจากงวดล่าสุด ─────────────
rand_triplet = random.choice(triplets)
thousands_from_latest = draws4[-1][0]  # หลักพันของงวดล่าสุด = ตัวแรกของสตริง 4 หลักล่าสุด
four_digit = thousands_from_latest + rand_triplet  # เช่น 9 + 122 → 9122

st.markdown("<div class='result-box'><div>4) เลขสี่ตัว 1 ชุด — สุ่มจากข้อ 3 แล้วใส่หลักพันของงวดล่าสุด</div>"
            f"<div class='small-red'>{four_digit}</div></div>", unsafe_allow_html=True)

# สรุปเล็ก ๆ
st.markdown("<hr class='sep'/>", unsafe_allow_html=True)
st.caption("หมายเหตุ: เป็นการวิเคราะห์เชิงสถิติ/ฮิวริสติก ไม่รับประกันผลลัพธ์จริง")
