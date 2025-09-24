# app.py
# -*- coding: utf-8 -*-
import re
import random
import streamlit as st
from collections import Counter

# ---------- Page config ----------
st.set_page_config(
    page_title="Lao Lotto — วิเคราะห์ & ทำนาย (4 หลัก)",
    page_icon="icon.png",
    layout="centered",
)

# ---------- (CSS) ขาว-แดง-น้ำเงิน ----------
st.markdown("""
<style>
/* พื้นหลังขาว */
.stApp { background:#ffffff; color:#111; }
.block-container { max-width: 860px; }

/* หัวข้อ/คำอธิบาย สีน้ำเงิน */
h1, .title-blue, .desc-blue { color:#0b5ed7 !important; }

/* กล่องผลลัพธ์ */
.card {
  background:#ffffff; border:2px solid #0b5ed7; border-radius:14px;
  padding:16px 18px; margin:12px 0;
}

/* ตัวเลขสีแดง */
.num-red { color:#d90429; font-weight:800; }

/* ขนาดตัวเลข: ข้อ 1 ใหญ่สุด */
.step1 { font-size: 3rem; line-height:1; }
.step2 { font-size: 1.8rem; }
.step3 { font-size: 1.8rem; }
.step4 { font-size: 1.8rem; }

/* ป้ายหัวการ์ด */
.card h3 { margin:0 0 6px 0; color:#0b5ed7; }

/* ปุ่ม */
.stButton>button { background:#0b5ed7; color:#fff; border:none; border-radius:10px; padding:0.6rem 1rem; }
.stButton>button:hover { background:#0a53be; }
</style>
""", unsafe_allow_html=True)

# ---------- หัวเรื่องสีน้ำเงิน ----------
st.markdown("<h1>🇱🇦 Lao Lotto — วิเคราะห์ & ทำนาย (4 หลัก)</h1>", unsafe_allow_html=True)
st.markdown("""
<div class="desc-blue">
วางเลข 4 หลัก ทีละบรรทัด (อย่างน้อย 10 งวด) — ระบบจะล้างอักขระอื่น ๆ และถ้าเกิน 4 หลักจะใช้ 4 หลักท้ายสุด วางเลข 4 หลัก
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- Input ----------
EXAMPLE = "6828\n0543\n0862\n9252\n9767\n5319"
raw = st.text_area("วางเลข 4 หลัก ทีละบรรทัด (อย่างน้อย 3 งวด)", value=EXAMPLE, height=220)

# ---------- Cleaning: เก็บ “4 หลักท้ายสุด” ของแต่ละบรรทัด ----------
def clean_to_last4(line: str) -> str | None:
    # ดึงเฉพาะตัวเลขทั้งหมด
    digits = re.findall(r"\d", line)
    if not digits:
        return None
    # ใช้ 4 หลักท้ายสุด
    last4 = "".join(digits[-4:])
    return last4 if len(last4) == 4 else None

lines = [ln for ln in raw.splitlines() if ln.strip()]
draws = []
for ln in lines:
    v = clean_to_last4(ln)
    if v is not None:
        draws.append(v)

st.write(f"✅ โหลดเลขที่ใช้ได้: **{len(draws)}** งวด")
if len(draws) < 3:
    st.warning("กรุณาวางเลขอย่างน้อย **3 งวด** เพื่อคำนวณตามกติกา")
    st.stop()

# ใช้ 3 งวดล่าสุดสำหรับขั้นตอน 1–2–4
last3 = draws[-3:]
# ใช้ 5 งวดล่าสุดสำหรับขั้นตอน 3
last5 = draws[-5:] if len(draws) >= 5 else draws[:]

# ---------- ขั้นตอน 1: เลือกเลขเดี่ยวจาก 'หลักสิบ & หลักหน่วย' ของ 3 งวดล่าสุด ----------
def pick_single_from_tens_units(last3_list):
    # ดึงหลักสิบ/หน่วยของแต่ละงวด (XY -> tens=X, units=Y จาก 4 หลัก ABCD: tens=C, units=D)
    pool = []
    for s in last3_list:
        tens = s[-2]   # หลักสิบ
        unit = s[-1]   # หลักหน่วย
        pool.extend([tens, unit])
    # เลือกตัวที่ถี่สุด; ถ้าเสมอ ให้เลือกตัวที่เกิด "ใกล้ปัจจุบันสุด" (ตามลำดับจากหลังไปหน้า)
    ctr = Counter(pool)
    maxc = max(ctr.values())
    cands = [d for d, c in ctr.items() if c == maxc]
    # เลือกด้วยหลัก tie-break: ปรากฏล่าสุดใน last3 (วนจากหลัง)
    for s in reversed(last3_list):
        if s[-2] in cands: chosen = s[-2]; break
        if s[-1] in cands: chosen = s[-1]; break
    return chosen

single_digit = pick_single_from_tens_units(last3)

# ---------- ขั้นตอน 2: ผสมเป็นเลขสองตัว จากตัวเลข “ทุกหลัก” ของ 3 งวดล่าสุด ----------
# เอาตัวเลขของ 3 งวดล่าสุด (ทั้ง 12 หลัก) เป็นลิสต์ตามลำดับเวลาจากเก่า->ใหม่
all_digits_last3 = []
for s in last3:
    all_digits_last3.extend(list(s))

# เรียงให้ “ไม่ซ้ำแต่คงลำดับการพบ”
partners_unique = []
for d in all_digits_last3:
    if d not in partners_unique:
        partners_unique.append(d)

# จับเลขพิเศษเป็นอันดับก่อน: 4,5,6,2,1,0
special_order = ['4', '5', '6', '2', '1', '0']
# สร้างลิสต์เป้าหมาย โดยเรียง special ก่อน ตามลำดับที่กำหนด แล้วตามด้วยตัวอื่นๆ ที่เหลือ
ordered_partners = []
for sp in special_order:
    if sp in partners_unique:
        ordered_partners.append(sp)
for d in partners_unique:
    if d not in ordered_partners:
        ordered_partners.append(d)

# สร้างคู่แบบ "single+partner"
pair_all = [single_digit + d for d in ordered_partners]
pairs_to_show = pair_all[:5]  # แสดงแค่ 5 ชุด

# ---------- ขั้นตอน 3: สร้างเลขสามตัว โดยเติม “เลขที่หายไปจาก 5 งวดล่าสุด” ไว้ด้านหน้า ----------
def missing_digit_from_last5(last5_list):
    seen = set()
    for s in last5_list:
        seen |= set(list(s))
    missing = [str(x) for x in range(10) if str(x) not in seen]
    if missing:
        return sorted(missing, key=lambda x: int(x))[0]  # เอาตัวเลขที่น้อยที่สุด
    # ถ้าไม่มีเลขหายไป ให้ใช้เลขที่ “พบน้อยสุด” ใน 5 งวดล่าสุดแทน
    ctr = Counter("".join(last5_list))
    minc = min(ctr.values())
    cands = [d for d, c in ctr.items() if c == minc]
    return sorted(cands, key=lambda x: int(x))[0]

prefix_digit = missing_digit_from_last5(last5)
triplets = [prefix_digit + p for p in pairs_to_show]   # ขนาดเท่ากับ pairs_to_show

# ---------- ขั้นตอน 4: สุ่มเลือกหนึ่งชุดจากข้อ 3 แล้วเอาหลักพันของงวดล่าสุดมาต่อหน้า ----------
random.seed()  # ไม่กำหนด seed ให้สุ่มจริง
picked3 = random.choice(triplets)
thousands = last3[-1][0]   # หลักพันของ "งวดล่าสุด"
four_digit = thousands + picked3

# ---------- แสดงผล (ฟอร์แมต/ขนาด/สี) ----------
st.markdown('<div class="card"><h3>1) เลขเดี่ยว (เลือกจากหลักสิบ/หน่วยของ 3 งวดล่าสุด)</h3>'
            f'<div class="num-red step1">{single_digit}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="card"><h3>2) เลขสองตัว (เลือกคัด 5 ชุด โดยจัดลำดับพิเศษ 4,5,6,2,1,0)</h3>'
            f'<div class="num-red step2">{", ".join(pairs_to_show)}</div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="card"><h3>3) เลขสามตัว (เติมเลขที่หายไปจาก 5 งวดล่าสุด: '
            f'<span class="num-red">{prefix_digit}</span> นำหน้า)</h3>'
            f'<div class="num-red step3">{", ".join(triplets)}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="card"><h3>4) เลขสี่ตัว (สุ่มเลือกจากข้อ 3 แล้วเติมหลักพันของงวดล่าสุด)</h3>'
            f'<div>เลขสามตัวที่สุ่มได้: <span class="num-red">{picked3}</span> '
            f'| หลักพันล่าสุด: <span class="num-red">{thousands}</span></div>'
            f'<div class="num-red step4" style="margin-top:8px;">' + four_digit + '</div></div>',
            unsafe_allow_html=True)

st.caption("หมายเหตุ: วิธีนี้เป็นฮิวริสติกเพื่อความบันเทิง ไม่รับประกันผลลัพธ์จริง")
