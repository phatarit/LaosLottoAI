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
.num-sm { color:var(--red); font-weight:900; font-size:1.9rem; line-height:1; }
.line { margin-top:8px; }
.bubble {
  display:inline-block; background:#fff; color:var(--red);
  border:2px solid var(--red); border-radius:12px;
  padding:4px 10px; margin:4px 6px 0 0; font-weight:900; font-size:1.4rem;
}
.note { font-size:0.9rem; color:#333; margin-top:6px; }
.kbd{ font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      background:#eef2ff; border:1px solid #c7d2fe; border-radius:6px; padding:2px 6px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Lao Lotto ทำนายจาก 5 งวด (ตามกติกาใหม่)</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "เช่น (เก่าสุด → ล่าสุด)\n8775\n3798\n6828\n0543\n0862"
raw = st.text_area("วางเลข 4 หลัก ทีละบรรทัด (ให้ครบ 5 งวด)", height=160, placeholder=ph)

# ดึงเฉพาะบรรทัดที่เป็นตัวเลข 4 หลัก
draws = []
for line in raw.splitlines():
    s = line.strip()
    if len(s) == 4 and s.isdigit():
        draws.append(s)
if len(draws) > 5:
    draws = draws[:5]  # ใช้ 5 รายการแรกที่ถูกต้อง

st.write(f"ข้อมูลที่อ่านได้: **{len(draws)} / 5** งวด")

if len(draws) < 5:
    st.warning("กรุณาวางเลขให้ครบ 5 งวด (ตัวเลข 4 หลัก)")
    st.stop()

# ----------------- เตรียมข้อมูล -----------------
# สมมติรูปแบบ: บรรทัดที่ 1 = เก่าสุด, บรรทัดที่ 5 = ล่าสุด
latest = draws[-1]  # งวดล่าสุด (ใช้ทุกข้อ)
digits_latest = [int(c) for c in latest]
mod10_latest = sum(digits_latest) % 10  # A ของข้อ 1–2
last_digit_latest = int(latest[-1])     # B ของข้อ 2

# นับความถี่เลข 0–9 ใน 5 งวด
all_digits = "".join(draws)
freq = Counter(all_digits)              # นับเป็นตัวอักษร '0'..'9'

# หา "เลขหายไป" ถ้ามี; ถ้าไม่มีให้ใช้ "เลขที่ออกน้อยสุด"
missing = [str(d) for d in range(10) if str(d) not in freq]
if missing:
    rare_digit = missing[0]  # เอาตัวแรกที่หายไป
else:
    # หาเลขที่ความถี่ต่ำสุด
    min_count = min(freq[str(d)] for d in range(10))
    rare_candidates = [str(d) for d in range(10) if freq[str(d)] == min_count]
    # เลือกตัวที่มีค่าน้อยสุดเพื่อคงความคงที่
    rare_digit = sorted(rare_candidates, key=int)[0]

# ----------------- ข้อ 1: เลขเดี่ยว (ผลรวม mod 10 ของงวดล่าสุด) -----------------
single_digit = str(mod10_latest)

# ----------------- ข้อ 2: เลขสองตัว (A+B) และ "5 ชุดที่ใกล้เคียงกัน"
# A = mod10 ล่าสุด, B = หลักสุดท้ายของงวดล่าสุด
A = mod10_latest
B = last_digit_latest

def wrap10(x): return (x + 10) % 10

# สร้าง 5 ชุดใกล้เคียง: คง A ไว้ ปรับ B เป็น B-2,B-1,B,B+1,B+2 (เวียน 0–9)
neighbors = [wrap10(B + k) for k in [-2, -1, 0, 1, 2]]
pairs_5 = [f"{A}{b}" for b in neighbors]
pair_base = f"{A}{B}"

# ----------------- ข้อ 3: เลขสามตัว
# เอาคู่ (จากข้อ 2) มาต่อหน้าด้วย: [เลขหายไป/ออกน้อยสุด] + [เลขพิเศษ 3,4,7,8,6] รวมเป็น 5 ชุด
specials = ['3', '4', '7', '8', '6']
front_pool = [rare_digit] + [d for d in specials if d != rare_digit]  # กันซ้ำถ้าบังเอิญตรงกัน
front_pool = front_pool[:5]

# ใช้คู่ฐานจากข้อ 2 เป็นแกน (ใช้คู่ตรงตัว A+B)
triples_5 = [f"{h}{pair_base}" for h in front_pool]

# ----------------- ข้อ 4: เลขสี่ตัว — Rotation + Fix หลักหน่วยเป็น mod10 ของงวดล่าสุด
# ทำจาก "งวดล่าสุด": ย้ายหลักสุดท้ายมาไว้หน้า แล้วแก้หลักหน่วยให้เท่ากับ mod10 ล่าสุด
rot = latest[-1] + latest[:-1]           # rotation 1 ตำแหน่ง (เอาหลักหน่วยขึ้นหน้า)
quad_fix = rot[:-1] + str(mod10_latest)  # แก้หลักหน่วย

# ----------------- OUTPUT -----------------
st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 1: เลขเดี่ยว (ผลรวม mod 10 ของงวดล่าสุด)</span>
  <div class="num-xl line">{single_digit}</div>
  <div class="note">ตัวอย่างคำนวณ: รวมเลข {latest[0]}+{latest[1]}+{latest[2]}+{latest[3]} = {sum(digits_latest)} → mod 10 = {mod10_latest}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 2: เลขสองตัว (A+B) และชุดใกล้เคียง</span>
  <div class="num-lg line">{pair_base}</div>
  <div class="note">A = mod10 ล่าสุด = <span class="kbd">{A}</span>, B = หลักสุดท้ายของ {latest} = <span class="kbd">{B}</span></div>
  <div class="line">{' '.join(f'<span class="bubble">{p}</span>' for p in pairs_5)}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 3: เลขสามตัว (เติมด้านหน้า)</span>
  <div class="note">เติมด้านหน้าด้วยเลขหายไป/ออกน้อยสุด = <span class="kbd">{rare_digit}</span> และเลขพิเศษ 3,4,7,8,6</div>
  <div class="num-md line">{'  '.join(triples_5)}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 4: เลขสี่ตัว (Rotation + Fix หลักหน่วย)</span>
  <div class="note">Rotation {latest} → <span class="kbd">{rot}</span> จากนั้นแก้หลักหน่วยให้เท่ากับ mod10 ล่าสุด (<span class="kbd">{mod
