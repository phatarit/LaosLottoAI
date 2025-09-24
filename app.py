# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import random
from collections import Counter

# ───────────────── Page config ─────────────────
st.set_page_config(
    page_title="Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด",
    page_icon="🇱🇦",
    layout="centered",
)

# ───────────────── Styles (white bg, red numbers, blue frames) ─────────────────
st.markdown("""
<style>
/* พื้นหลังขาว ตัวอักษรหลักน้ำเงิน */
.stApp { background: #ffffff; color: #0a1f55; }
.block-container { max-width: 860px; }

/* ชื่อแอป สีฟ้า/น้ำเงิน */
h1, .title-blue { color:#0a4cc5 !important; }

/* กรอบสีน้ำเงิน */
.blue-box {
  border:2px solid #0a4cc5; border-radius:14px; padding:14px 18px; margin:12px 0;
  background:#f7fbff;
}

/* ป้ายชื่อขั้น (เด่น/เจาะ/เน้น/รวย) */
.step-tag {
  display:inline-block; background:#0a4cc5; color:#fff; padding:4px 10px;
  border-radius:999px; font-weight:700; letter-spacing:.5px; margin-bottom:6px;
}

/* ตัวเลขสีแดง + สเกลขนาด */
.num-red { color:#d9152a; line-height:1.05; font-weight:800; }
.num-xxl { font-size:4rem; }       /* ใหญ่สุด: เด่น */
.num-xl  { font-size:2.8rem; }     /* เจาะ */
.num-lg  { font-size:2.4rem; }     /* เน้น */
.num-md  { font-size:2.2rem; }     /* รวย (สุดท้าย) */
.nums-row { display:flex; flex-wrap:wrap; gap:14px; }

/* ตัวเลขเป็นชิป */
.chip {
  background:#fff; border:2px solid #0a4cc5; color:#d9152a;
  padding:6px 14px; border-radius:12px; font-weight:800; font-size:2.2rem;
}

/* ช่องกรอก */
textarea, .stTextArea textarea { background:#ffffff; color:#0a1f55;
  border:2px solid #0a4cc5; border-radius:12px; }

/* ปล. ไม่มีคำอธิบายใต้ตัวเลขตามโจทย์ */
</style>
""", unsafe_allow_html=True)

# ───────────────── Title ─────────────────
st.markdown("<h1 class='title-blue'>Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด</h1>", unsafe_allow_html=True)

# ───────────────── Input ─────────────────
placeholder = "8775\n3798\n6828\n0543\n0862"
raw = st.text_area("วางเลข 4 หลัก ทีละบรรทัด (ต้อง 5 งวด)", value=placeholder, height=150)
lines = [s.strip() for s in raw.splitlines() if s.strip()]
valid = [s for s in lines if len(s)==4 and s.isdigit()]

if len(valid) != 5:
    st.stop()

# ใช้ 5 งวดล่าสุดตามลำดับที่วาง (บน→ล่าง = เก่า→ใหม่)
draws = valid[-5:]              # list of 5 เช่น ["8775","3798","6828","0543","0862"]
d1, d2, d3, d4, d5 = draws      # d5 = ล่าสุด

# ───────────────── Step 1: เลขเดี่ยว = หลักสิบ+หน่วยของงวดที่ 3 ─────────────────
tens  = d3[2]
ones  = d3[3]
singles = [tens, ones] if tens != ones else [tens]  # กรณีซ้ำให้แสดงตัวเดียว

# ───────────────── Step 2: เจาะ = สร้างเลขสองตัวจากเลขเดี่ยว × (ตัวเลขที่พบใน 3 งวดล่าสุด) ─────────────────
# 3 งวดล่าสุด = d3, d4, d5 (ตามตัวอย่างโจทย์แต่จะยึด "ก่อนหน้าล่าสุด 3 งวด" = สามงวดท้าย)
last3_digits = []
for s in [d3, d4, d5]:
    last3_digits.extend(list(s))

# เอาไม่ซ้ำตามลำดับปรากฏ
partners_ordered = []
for ch in last3_digits:
    if ch not in partners_ordered:
        partners_ordered.append(ch)

# คัดเฉพาะ "เลขพิเศษ" แล้วจำกัด 5 ชุด
special = ["4","5","6","2","1","0"]

def pick_pairs(lead: str):
    cands = [lead + p for p in partners_ordered if p in special]
    # ถ้าตัวพิเศษไม่พอ ให้เติมตามลำดับ special ที่เหลืออยู่
    if len(cands) < 5:
        for p in special:
            pair = lead + p
            if pair not in cands:
                cands.append(pair)
            if len(cands) == 5:
                break
    return cands[:5]

pairs_map = {lead: pick_pairs(lead) for lead in singles}

# ───────────────── Step 3: เน้น = สามตัว โดยใส่ "เลขที่หายไป" 5 งวดล่าสุดไว้ด้านหน้า ─────────────────
all5_digits = list("".join(draws))
miss = [d for d in "0123456789" if d not in set(all5_digits)]
if not miss:
    # ถ้าไม่มีเลขหายไป เลือกตัวที่ "พบต่ำสุด" (นับรวมทั้ง 5 งวด)
    cnt = Counter(all5_digits)
    minc = min(cnt.values())
    miss = sorted([d for d,c in cnt.items() if c==minc], key=lambda x:int(x))
prefix = miss[0]  # เอาตัวแรก (คงเสถียร)

triples_map = {lead: [prefix + pp for pp in pairs_map[lead]] for lead in pairs_map}

# ───────────────── Step 4: รวย = สี่ตัว 1 ชุด (สุ่ม 1 สามตัว จากข้อ 3) + หลักพันของงวดล่าสุด ─────────────────
thousands_latest = d5[0]
random.seed()  # สุ่มไม่เจาะจง
any_triple = random.choice(sum(triples_map.values(), []))  # สุ่มหนึ่งชุดจากทั้งหมด
four_digit = thousands_latest + any_triple  # ใส่หลักพัน

# ───────────────── Render (เฉพาะตัวเลข + คำ: เด่น/เจาะ/เน้น/รวย) ─────────────────
# เด่น
st.markdown("<div class='blue-box'><span class='step-tag'>เด่น</span><div class='nums-row'>"
            + "".join([f"<div class='num-red num-xxl'>{s}</div>" for s in singles])
            + "</div></div>", unsafe_allow_html=True)

# เจาะ (แสดงเป็นกลุ่มต่อเลขเดี่ยว)
for lead in singles:
    st.markdown("<div class='blue-box'><span class='step-tag'>เจาะ</span><div class='nums-row'>"
                + "".join([f"<div class='chip'>{p}</div>" for p in pairs_map[lead]])
                + "</div></div>", unsafe_allow_html=True)

# เน้น (สามตัวจากแต่ละเด่น)
for lead in singles:
    st.markdown("<div class='blue-box'><span class='step-tag'>เน้น</span><div class='nums-row'>"
                + "".join([f"<div class='chip'>{t}</div>" for t in triples_map[lead]])
                + "</div></div>", unsafe_allow_html=True)

# รวย (สี่ตัว 1 ชุด)
st.markdown("<div class='blue-box'><span class='step-tag'>รวย</span>"
            f"<div class='num-red num-md'>{four_digit}</div></div>", unsafe_allow_html=True)

# ลิขสิทธิ์
st.caption("© ผู้สร้าง: Lao Lotto — ใช้เพื่อการทดลองเชิงสถิติเท่านั้น")
