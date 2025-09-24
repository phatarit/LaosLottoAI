# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import random

# ── CONFIG ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lao Lotto — วางเลข 4 หลัก ทีละบรรทัด 5 งวด",
    page_icon="icon.png",
    layout="centered"
)

# ── THEME (พื้นขาว ตัวเลขแดง, หัวข้อสีน้ำเงิน) ─────────────────
st.markdown("""
<style>
.stApp { background:#ffffff; color:#111; }
.block-container { max-width: 820px; }
h1.title { color:#0b53b6; margin-bottom: .25rem; }
.subtitle { color:#0b53b6; margin: 0 0 1rem 0; font-weight:700; }
.panel { border:2px solid #0b53b6; border-radius:18px; padding:16px 18px; }
.row { display:flex; flex-direction:column; gap:14px; }
.badge { background:#0b53b6; color:#fff; padding:3px 10px; border-radius:999px; display:inline-block; font-weight:700; }
.item { border:2px solid #0b53b6; border-radius:14px; padding:10px 14px; }
.k1, .k2, .k3, .k4 { color:#d81616; font-weight:900; line-height:1; display:block; }
.k1 { font-size:64px; letter-spacing:2px; }
.k2 { font-size:44px; }
.k3 { font-size:36px; }
.k4 { font-size:32px; }
.label { color:#0b53b6; font-weight:800; font-size:18px; margin-bottom:6px; }
.err { color:#b00020; font-weight:700; }
textarea, .stTextArea textarea { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────
st.markdown('<h1 class="title">Lao Lotto</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">วางเลข 4 หลัก ทีละบรรทัด 5 งวด</div>', unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────
sample = "8775\n3798\n6828\n0543\n0862"
raw = st.text_area("ใส่เลข 4 หลัก ทีละบรรทัด (5 งวด)", value=sample, height=140)

# ── PARSE ─────────────────────────────────────────────────────────
lines = [s.strip() for s in raw.splitlines() if s.strip()]
valid = [s for s in lines if s.isdigit() and len(s) == 4]

if len(valid) != 5:
    st.markdown('<div class="err">กรุณาใส่เลข 4 หลักให้ครบ 5 บรรทัด (ตัวเลขเท่านั้น)</div>', unsafe_allow_html=True)
    st.stop()

# งวดเรียงตามที่วาง: [งวด1, งวด2, งวด3, งวด4, งวด5]
d1, d2, d3, d4, d5 = valid

# ── LOGIC ─────────────────────────────────────────────────────────
# 1) เลขเดี่ยว = หลักสิบและหลักหน่วยของ "งวดที่ 3"
single_a = d3[-2]  # tens
single_b = d3[-1]  # ones
singles = [single_a, single_b]  # ตัวเลขเด่น 2 ตัว

# 2) นำเลขเด่นไปจับกับเลขของ "2 งวดก่อนหน้า" (งวด4, งวด5) เพื่อสร้างเลขสองตัว
prev_digits = list(dict.fromkeys(list(d4 + d5)))  # รักษาลำดับ & ไม่ซ้ำ
pairs_all = []
for s in singles:
    for p in prev_digits:
        pairs_all.append(s + p)

# คัดคู่ที่มีเลขพิเศษ {4,5,6,2,1,0}
special = set(list("456210"))
pairs_filtered = [p for p in pairs_all if (set(p) & special)]

# สุ่ม 5 ชุด (ไม่ซ้ำ) ถ้าไม่พอให้เติมจากทั้งหมด
random.seed()  # ใช้ seed ระบบ
choices = list(dict.fromkeys(pairs_filtered))  # unique ตามลำดับ
if len(choices) < 5:
    # เติมจาก pairs_all ให้ครบ 5
    for p in pairs_all:
        if p not in choices:
            choices.append(p)
        if len(choices) >= 5:
            break
pairs_pick5 = random.sample(choices, k=min(5, len(choices)))
if len(pairs_pick5) < 5:
    # ถ้ายังไม่ครบ (กรณีข้อมูลจำกัด) ให้คัดเพิ่มซ้ำได้
    while len(pairs_pick5) < 5:
        pairs_pick5.append(random.choice(choices))

# 3) เลขสามตัว = ใส่ "เลขที่หายไปใน 5 งวดล่าสุด" ด้านหน้า (ถ้าไม่มี ให้ใช้เลขที่พบน้อยที่สุด)
digits_seen = set("".join(valid))
missing = [str(i) for i in range(10) if str(i) not in digits_seen]
if missing:
    prefix = missing[0]  # ตัวแรก
else:
    # หาเลขที่พบน้อยที่สุด
    from collections import Counter
    cnt = Counter("".join(valid))
    minc = min(cnt.values())
    prefix = sorted([d for d, c in cnt.items() if c == minc])[0]

triples = [prefix + p for p in pairs_pick5]

# 4) เลขสี่ตัว (1 ชุด) = สุ่มเลือกหนึ่งชุดจากข้อ 3 แล้วเอา "หลักพัน" ของงวดล่าสุด (งวด5) มาใส่หน้า
thousands = d5[0]
triple_choice = random.choice(triples)
quad = thousands + triple_choice

# ── DISPLAY (เลขสีแดง, พื้นขาว, ตัวใหญ่ลดหลั่น, หัวข้อ/กรอบสีน้ำเงิน) ──────────────
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<span class="badge">กรอบผลลัพธ์</span>', unsafe_allow_html=True)
st.markdown('<div class="row">', unsafe_allow_html=True)

# เด่น
st.markdown(f'''
<div class="item">
  <div class="label">เด่น</div>
  <span class="k1">{singles[0]} {singles[1]}</span>
</div>
''', unsafe_allow_html=True)

# เจาะ
st.markdown(f'''
<div class="item">
  <div class="label">เจาะ</div>
  <span class="k2">{", ".join(pairs_pick5)}</span>
</div>
''', unsafe_allow_html=True)

# เน้น
st.markdown(f'''
<div class="item">
  <div class="label">เน้น</div>
  <span class="k3">{", ".join(triples)}</span>
</div>
''', unsafe_allow_html=True)

# รวย
st.markdown(f'''
<div class="item">
  <div class="label">รวย</div>
  <span class="k4">{quad}</span>
</div>
''', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
