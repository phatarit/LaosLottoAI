# app.py
# -*- coding: utf-8 -*-
import re
import random
from collections import Counter

import streamlit as st

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Lao Lotto — Smart Picks (4 digits)",
    page_icon="🇱🇦",
    layout="centered",
)

# ---------------- Theme (white bg, red numbers, blue borders) ----------------
st.markdown("""
<style>
.stApp { background:#ffffff; color:#111; }
.block-container { max-width:900px; }
.box {
  border:2px solid #0b5bd3; border-radius:14px; padding:14px 16px; margin:12px 0;
  background:#fff;
}
.big    { font-size:3.2rem; font-weight:800; color:#d41414; letter-spacing:1px; }
.mid    { font-size:2.2rem; font-weight:800; color:#d41414; letter-spacing:1px; }
.small  { font-size:1.8rem; font-weight:800; color:#d41414; letter-spacing:1px; }
.label  { font-size:0.95rem; color:#0b5bd3; font-weight:700; text-transform:uppercase; }
.note   { color:#666; font-size:0.9rem; }
hr { border-color:#e7eefb; }
</style>
""", unsafe_allow_html=True)

st.title("🇱🇦 Lao Lotto — วิเคราะห์ & ทำนาย 4 หลัก")

st.write("วางเลข **4 หลัก/บรรทัด** อย่างน้อย **5 งวด** (ตัวอื่น ๆ ในบรรทัดจะถูกตัดทิ้ง เก็บเฉพาะกลุ่มตัวเลข 4 หลักท้ายบรรทัด)")

# ---------------- Input ----------------
sample = "0543\n0862\n9252\n9767\n5319"
raw = st.text_area("วางเลข 4 หลัก", value=sample, height=180, placeholder="เช่น 0543\n0862\n9252 ...")

lines = [ln for ln in raw.splitlines() if ln.strip()]

def extract_last_4digits(s: str) -> str | None:
    """คืนกลุ่มตัวเลข 4 หลัก 'สุดท้าย' ในบรรทัดนั้น ถ้าไม่มีคืน None"""
    groups = re.findall(r"(\d{4})", s)
    return groups[-1] if groups else None

draws_all = []
for ln in lines:
    d = extract_last_4digits(ln.strip())
    if d: draws_all.append(d)

st.write(f"โหลดข้อมูลที่ใช้งานได้: **{len(draws_all)}** งวด → " +
         (", ".join(draws_all[-10:]) if draws_all else "—"))

if len(draws_all) < 5:
    st.warning("กรุณาใส่อย่างน้อย **5 งวด** จึงจะเริ่มวิเคราะห์ได้")
    st.stop()

# ---------------- Core helpers ----------------
def digits_from_draws(draws: list[str]) -> list[str]:
    out = []
    for d in draws:
        out.extend(list(d))
    return out

def most_frequent_digit(last5: list[str]) -> str:
    c = Counter(digits_from_draws(last5))
    # หากเสมอกัน เลือกตัวที่มาก่อนตามลำดับตัวเลข
    top_cnt = max(c.values())
    candidates = sorted([d for d, n in c.items() if n == top_cnt], key=lambda x: int(x))
    return candidates[0]

def partner_digits_from_last3(last3: list[str]) -> list[str]:
    """คืนตัวเลขแบบ unique รักษาลำดับที่ปรากฏ จาก 3 งวดล่าสุด (รวม 12 หลัก)"""
    seen = set()
    ordered = []
    for d in "".join(last3):
        if d not in seen:
            seen.add(d); ordered.append(d)
    return ordered

def select_top5_pairs(hot: str, partners: list[str]) -> list[str]:
    """
    สร้างเลข 2 หลัก hot+digit แล้วคัด 5 ชุด
    - จัดลำดับพิเศษ: 4,5,6,2,1,0 มาก่อน (ถ้าอยู่ใน partners)
    - จากนั้นตามลำดับที่เหลือใน partners เดิม
    - อนุญาตคู่ซ้ำเช่น 22 ได้ (ถ้า digit == hot และอยู่ใน partners)
    """
    special_order = ['4','5','6','2','1','0']
    preferred = [d for d in special_order if d in partners]
    others    = [d for d in partners if d not in preferred]
    order = preferred + others
    pairs = [hot + d for d in order]
    # คัด 5 ชุดแรก
    return pairs[:5]

def missing_digit_in_last5(last5: list[str]) -> str:
    used = set(digits_from_draws(last5))
    missing = [str(d) for d in range(10) if str(d) not in used]
    if missing:
        return sorted(missing, key=lambda x:int(x))[0]
    # ถ้าไม่มีที่หายไป ใช้ตัวที่พบน้อยสุดแทน
    c = Counter(digits_from_draws(last5))
    min_cnt = min(c.values())
    leasts = sorted([d for d, n in c.items() if n == min_cnt], key=lambda x:int(x))
    return leasts[0]

# ---------------- Compute per spec ----------------
last5 = draws_all[-5:]               # ใช้หา hot & missing
last3 = draws_all[-3:]               # ใช้เป็นแหล่ง partner
latest_draw = draws_all[-1]          # ใช้หลักพันข้อ 4

# 1) เลขเดี่ยวถี่สุดใน 5 งวด
hot = most_frequent_digit(last5)

# 2) จับคู่กับเลขจาก 3 งวดล่าสุด → คัด 5 ชุด โดยให้ 4,5,6,2,1,0 มาก่อน
partners = partner_digits_from_last3(last3)
pairs_2d = select_top5_pairs(hot, partners)

# 3) หาเลขที่หายไปจาก 5 งวด → ใส่เป็นหลักหน้า
missing = missing_digit_in_last5(last5)
triples = [missing + p for p in pairs_2d]

# 4) สุ่ม 3 ตัว 1 ชุด แล้วใช้ “หลักพัน” จากงวดล่าสุด (ตัวแรกของงวดล่าสุด)
random.seed()               # ใช้ระบบสุ่มพื้นฐาน
pick3 = random.choice(triples)
thousand = latest_draw[0]   # หลักพันของงวดล่าสุด = ตัวแรกของสตริง 4 หลักล่าสุด
four_digit = thousand + pick3

# ---------------- Display ----------------
st.markdown("<div class='box'><div class='label'>1) เลขเดี่ยว (เกิดถี่สุด ใน 5 งวด)</div>"
            f"<div class='big'>{hot}</div></div>", unsafe_allow_html=True)

st.markdown("<div class='box'><div class='label'>2) เลขสองตัว (จากเลขเดี่ยว × 3 งวดล่าสุด, คัดพิเศษ 4,5,6,2,1,0)</div>"
            f"<div class='mid'>{', '.join(pairs_2d)}</div>"
            "<div class='note'>ตัวอย่างวิธีคัด: ถ้า hot=2 และ 3 งวดล่าสุดมี 0,1,2,3,4,5,6..."
            " จะเรียง 24,25,26,22,20 แล้วค่อยตัวอื่น ๆ</div></div>", unsafe_allow_html=True)

st.markdown("<div class='box'><div class='label'>3) เลขสามตัว (เติมเลขที่หายไปใน 5 งวดเป็นหลักหน้า)</div>"
            f"<div class='mid'>{', '.join(triples)}</div>"
            f"<div class='note'>เลขที่หายไปที่ใช้เติม: {missing}</div></div>", unsafe_allow_html=True)

st.markdown("<div class='box'><div class='label'>4) เลขสี่ตัว 1 ชุด (สุ่มจากข้อ 3 แล้วเติมหลักพันจากงวดล่าสุด)</div>"
            f"<div class='small'>{four_digit}</div>"
            f"<div class='note'>เลือกสามตัวแบบสุ่ม: {pick3} | หลักพันจากงวดล่าสุด ({latest_draw}) = {thousand}</div></div>",
            unsafe_allow_html=True)
