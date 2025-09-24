# app.py
# -*- coding: utf-8 -*-
import re
import random
from collections import Counter
import streamlit as st

# ───────────── CONFIG ─────────────
st.set_page_config(
    page_title="Lao Lotto — Analyzer",
    page_icon="🇱🇦",
    layout="centered"
)

# ───────────── THEME (ตัวเลขแดง พื้นขาว กรอบน้ำเงิน) ─────────────
st.markdown("""
<style>
.stApp { background: #ffffff; }
.block-container { max-width: 860px; }
.card {
  background: #fff; border: 2px solid #1f4fbf; border-radius: 14px;
  padding: 14px 16px; margin: 10px 0;
}
.big   { font-size: 3rem;   color: #d70000; font-weight: 800; text-align:center; }
.huge  { font-size: 4rem;   color: #d70000; font-weight: 900; text-align:center; }
.mid   { font-size: 2.1rem; color: #d70000; font-weight: 800; text-align:center; }
.listnum { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; }
.pill {
  font-size: 2rem; color:#d70000; font-weight:800;
  border:2px solid #1f4fbf; border-radius:12px; padding:6px 16px; background:#fff;
}
.note { color:#3b3b3b; font-size:0.95rem; }
hr { border-color:#c8d6ff; }
</style>
""", unsafe_allow_html=True)

st.title("🇱🇦 Lao Lotto — วิเคราะห์ & ทำนาย (4 หลัก)")

st.markdown(
    "วางเลข **4 หลัก** ทีละบรรทัด (อย่างน้อย 10 งวด) — ระบบจะล้างอักขระอื่น ๆ และถ้าเกิน 4 หลักจะใช้ **4 หลักท้ายสุด**"
)

# ───────────── INPUT ─────────────
sample = "9767\n5319\n1961\n4765\n2633\n3565\n0460\n0619\n2059\n4973"
raw = st.text_area("วางเลข 4 หลัก", height=220, placeholder=sample)

def parse_lines_to_4digits(lines):
    out = []
    for ln in lines:
        s = re.sub(r"\D", "", ln)  # เก็บเฉพาะตัวเลข
        if len(s) >= 4:
            out.append(s[-4:])     # หยิบ 4 หลักท้ายสุด
    return out

lines = [x for x in raw.splitlines() if x.strip()]
draws = parse_lines_to_4digits(lines)
st.write(f"โหลดข้อมูลที่ตีความเป็นเลข 4 หลักได้: **{len(draws)}** งวด")

if len(draws) < 10:
    st.warning("กรุณาใส่อย่างน้อย **10 งวด**")
    st.stop()

# ใช้ 10 งวดล่าสุดตามสเปกของข้อวิเคราะห์
last10 = draws[-10:]
last3  = draws[-3:]  # สำหรับข้อ 2

# ───────────── HELPERS ─────────────
def most_frequent_digit_in_draws(draw_list):
    c = Counter()
    for d in draw_list:
        c.update(list(d))
    # tie-break โดยเลือกตัวเลขที่น้อยที่สุด
    return min([d for d, cnt in c.items() if cnt == max(c.values())], key=int), c

def unique_digits_from_draws(draw_list):
    """คืน list ของตัวเลข (ตัวอักษร '0'-'9') รักษาลำดับการพบจากขวาไปซ้ายตามงวดล่าสุดก่อน"""
    seq = []
    for d in draw_list[::-1]:  # เริ่มจากงวดล่าสุดสุดก่อนเพื่อให้ลำดับล่าสุดนำ
        for ch in d:
            if ch not in seq:
                seq.append(ch)
    return seq[::-1]  # กลับลำดับให้เก่ากว่าอยู่ซ้าย (เพื่อความอ่านง่าย)

def missing_digits_from_last_k(draw_list, k=5):
    recent = draw_list[-k:]
    seen = set("".join(recent))
    return [str(x) for x in range(10) if str(x) not in seen]

def pairs_from_hot_and_prev3(hot, prev3):
    """
    - ดึงตัวเลขทั้งหมดจาก 3 งวดล่าสุด (คงลำดับแต่ตัดซ้ำ)
    - จัดลำดับให้ "เลขพิเศษ: 4,5,6,2,1,0" มาก่อนถ้าอยู่ในชุด
    - สร้างเลขสองตัว = hot + partner
    - จำกัดแสดง 5 ชุด
    """
    # ตัวเลข 3 งวดล่าสุด (คงลำดับ)
    partners = []
    for d in prev3:
        for ch in d:
            if ch not in partners:
                partners.append(ch)

    # จัด priority สำหรับเลขพิเศษ
    special_order = ['4', '5', '6', '2', '1', '0']
    special = [p for p in special_order if p in partners]
    others  = [p for p in partners if p not in special_order]

    ordered = special + others

    pairs = []
    for p in ordered:
        val = hot + p
        if val not in pairs:
            pairs.append(val)
        if len(pairs) == 5:
            break

    # fallback: ถ้ายังไม่ครบ 5 (กรณี partners น้อยมาก)
    if len(pairs) < 5:
        for d in "0123456789":
            if d not in ordered:
                val = hot + d
                if val not in pairs:
                    pairs.append(val)
                if len(pairs) == 5:
                    break
    return pairs

# ───────────── 1) เลขเดี่ยว (เกิดถี่สุด) ใน 10 งวดล่าสุด ─────────────
hot_digit, freq_counter = most_frequent_digit_in_draws(last10)

st.markdown("<div class='card'><div class='huge'>เลขเดี่ยว (เกิดถี่สุด): "
            f"{hot_digit}</div></div>", unsafe_allow_html=True)

# ───────────── 2) ผสมกับเลขจาก 3 งวดล่าสุด → เลขสองตัว (คัดพิเศษ 4,5,6,2,1,0) ─────────────
pairs = pairs_from_hot_and_prev3(hot_digit, last3)
st.markdown("<div class='card'><div class='mid'>เลขสองตัว (คัดมา 5 ชุด)</div>"
            "<div class='listnum'>" +
            "".join([f"<div class='pill'>{p}</div>" for p in pairs]) +
            "</div></div>", unsafe_allow_html=True)

# ───────────── 3) เลขสามตัว: เติม “เลขที่หายไปจาก 5 งวดล่าสุด” ไว้ข้างหน้า ─────────────
missing = missing_digits_from_last_k(draws, k=5)
if missing:
    prefix = sorted(missing, key=int)[0]  # เลือกตัวเล็กสุดเพื่อคงที่
else:
    # ถ้าไม่มีเลขหายไปเลย ให้ใช้ตัวที่พบน้อยสุดใน 5 งวดล่าสุดแทน
    c5 = Counter("".join(draws[-5:]))
    min_cnt = min(c5.values())
    prefix = sorted([d for d, cnt in c5.items() if cnt == min_cnt], key=int)[0]

triplets = [prefix + p for p in pairs]

st.markdown("<div class='card'><div class='mid'>เลขสามตัว</div>"
            "<div class='listnum'>" +
            "".join([f"<div class='pill'>{t}</div>" for t in triplets]) +
            "</div><div class='note'>เลขที่หายไป (5 งวดล่าสุด): "
            f"{', '.join(missing) if missing else '— (ใช้เลขพบน้อยสุดแทน)'}"
            "</div></div>", unsafe_allow_html=True)

# ───────────── 4) เลขสี่ตัว 1 ชุด (สุ่มเลือกหนึ่งชุดจากข้อ 3 + เอาหลักพันงวดล่าสุดมาใส่หน้า) ─────────────
chosen3 = random.choice(triplets)
thousands = last3[-1][0]  # หลักพันของ “งวดล่าสุด”
four_digit = thousands + chosen3

st.markdown("<div class='card'><div class='mid'>เลขสี่ตัว (1 ชุด)</div>"
            f"<div class='big'>{four_digit}</div>"
            "<div class='note'>สุ่มจากเลขสามตัวข้างต้น แล้วใช้หลักพันของงวดล่าสุดมาใส่หน้า</div>"
            "</div>", unsafe_allow_html=True)

# ───────────── (เสริม) สรุปความถี่ 0–9 ใน 10 งวดล่าสุด ─────────────
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("**ความถี่ตัวเลข (0–9) จาก 10 งวดล่าสุด**")
freq10 = Counter("".join(last10))
freq_line = " ".join([f"<span class='pill' style='font-size:1.3rem'>{d}:{freq10.get(str(d),0)}</span>" for d in range(10)])
st.markdown(f"<div class='card' style='text-align:center'>{freq_line}</div>", unsafe_allow_html=True)

st.caption("หมายเหตุ: เป็นการวิเคราะห์เชิงฮิวริสติกเพื่อความบันเทิง ไม่รับประกันผลลัพธ์จริง")
