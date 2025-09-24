# app.py
# -*- coding: utf-8 -*-
import random
import streamlit as st

st.set_page_config(
    page_title="Lao Lotto — วิเคราะห์ & ทำนาย (4 หลัก)",
    page_icon="🇱🇦",
    layout="centered",
)

# ----------------------- THEME (ขาว-น้ำเงิน-แดง) -----------------------
st.markdown("""
<style>
:root{
  --blue:#0b58b0; --red:#d82020; --bord:#0b58b0; --light:#ffffff; --text:#0b58b0;
}
.stApp { background: var(--light); color:#222; }
.block-container{ max-width: 900px; }
.title-blue{ color:var(--blue); margin-bottom: .25rem;}
.subtitle{ color:var(--blue); margin-top:.25rem; opacity:.9; }
.card{
  background:#fff; border:2px solid var(--bord); border-radius:14px;
  padding:14px 16px; margin:12px 0;
}
.num{
  display:inline-block; color:var(--red); background:#fff; border:2px solid var(--bord);
  border-radius:12px; padding:.35rem .65rem; margin:.25rem .25rem; font-weight:800;
  letter-spacing:.5px;
}
.num.big{ font-size: 2.6rem; }
.num.mid{ font-size: 1.8rem; }
.num.sm { font-size: 1.4rem; }
.help{ color:#4a4a4a; font-size:.9rem; }
textarea, .stTextArea textarea{
  background:#fff !important; color:#111 !important; border:2px solid var(--bord) !important;
  border-radius:12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title-blue">Lao Lotto — วิเคราะห์ & ทำนาย (4 หลัก)</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">วางเลข 4 หลัก ทีละบรรทัด 3 งวด</div>', unsafe_allow_html=True)

# ----------------------- INPUT -----------------------
DEFAULT = "6828\n0543\n0862"  # ตัวอย่างขั้นต่ำ 3 งวด (เปลี่ยน/วางจริงทับได้)
raw = st.text_area("วางเลข 4 หลัก (อย่างน้อย 3 งวด)", value=DEFAULT, height=160,
                   placeholder="เช่น\n6828\n0543\n0862\n...")

lines = [s.strip() for s in raw.splitlines() if s.strip()]
draws = [s for s in lines if s.isdigit() and len(s) == 4]

colA, colB = st.columns([1,1])
with colA:
    pick_source = st.radio("เลือกระหว่างหลักสิบ/หลักหน่วยของงวดที่ 1 (ข้อ 1)", ["หลักสิบ", "หลักหน่วย"], horizontal=True)
with colB:
    seed = st.number_input("Random seed (ใช้สำหรับสุ่มในข้อ 4)", min_value=0, value=0, step=1)

# ----------------------- VALIDATION -----------------------
if len(draws) < 3:
    st.warning("กรุณาวางเลข **อย่างน้อย 3 งวด** (แต่ละบรรทัดเป็นเลข 4 หลัก)")
    st.stop()

# ใช้ 3 งวดล่าสุดในการอ้างอิงตามโจทย์
last3 = draws[-3:]
first_of_3 = last3[0]     # งวดที่ 1 (จาก 3 งวดล่าสุด)
latest = last3[-1]        # งวดล่าสุด (ใช้หลักพันในข้อ 4)

# ----------------------- STEP 1 -----------------------
# ข้อ 1: เลือก 1 เลขจากหลักสิบ/หลักหน่วยของงวดที่ 1
tens = first_of_3[-2]     # หลักสิบ
ones = first_of_3[-1]     # หลักหน่วย
single_pick = tens if pick_source == "หลักสิบ" else ones

st.markdown('<div class="card"><div class="help">ข้อ 1 — เลขเดี่ยวจากงวดที่ 1 (เลือกจากหลักสิบ/หลักหน่วย)</div>'
            f'<span class="num big">{single_pick}</span> '
            f'<span class="help">(จากงวดที่ 1 = {first_of_3})</span></div>', unsafe_allow_html=True)

# ----------------------- STEP 2 -----------------------
# ข้อ 2: สร้างเลขสองตัวจากเลขเดี่ยว + ตัวเลขที่พบใน 3 งวดที่ผ่านมา (unique ตามลำดับที่พบ)
# จากตัวอย่าง 0543,0862,9252 -> รวมตัวเลขที่พบแบบไม่ซ้ำ: 0,5,4,3,8,6,2,9
partners_in_order = []
seen = set()
for draw in last3:
    for d in draw:
        if d not in seen:
            partners_in_order.append(d)
            seen.add(d)

# สร้างคู่ 2X โดย X คือ partners
pairs_all = [f"{single_pick}{d}" for d in partners_in_order if d != single_pick]

# แต่ “ให้คัดมาแสดงแค่ 5 ชุด” โดย “ให้จับเลขพิเศษ 4,5,6,2,1,0” มาก่อน
special_order = ['4','5','6','2','1','0']
# เก็บตามลำดับพิเศษก่อน แล้วค่อยเติมที่เหลือ
pairs_special = [f"{single_pick}{d}" for d in special_order if d in seen and d != single_pick]
# เติมส่วนที่เหลือจาก partners_in_order
pairs_rest = [p for p in pairs_all if p not in pairs_special]
pairs_final_5 = (pairs_special + pairs_rest)[:5]

st.markdown('<div class="card"><div class="help">ข้อ 2 — เลขสองตัว (เน้นเลขพิเศษ 4,5,6,2,1,0 มาก่อน / แสดงสูงสุด 5 ชุด)</div>'
            + " ".join([f'<span class="num mid">{p}</span>' for p in pairs_final_5])
            + '</div>', unsafe_allow_html=True)

# ----------------------- STEP 3 -----------------------
# ข้อ 3: เลขสามตัว = ใส่เลขที่หายไปจาก 5 งวดล่าสุดไว้ด้านหน้า
last5 = draws[-5:] if len(draws) >= 5 else draws[:]   # เผื่อกรณีน้อยกว่า 5 จะใช้ทั้งหมด
seen5 = set("".join(last5))
missing = [str(d) for d in range(10) if str(d) not in seen5]

if missing:
    prefix = sorted(missing, key=lambda x: int(x))[0]   # เอาตัวเล็กสุดเพื่อเสถียร
    reason = f"เลขที่หายไปจาก {len(last5)} งวดล่าสุด: {', '.join(sorted(missing, key=lambda x:int(x)))}"
else:
    # ถ้าไม่มีเลขที่หายไป ให้ใช้เลขที่พบน้อยสุดใน 5 งวด
    from collections import Counter
    c5 = Counter("".join(last5))
    minc = min(c5.values())
    candidates = [d for d, c in c5.items() if c == minc]
    prefix = sorted(candidates, key=lambda x: int(x))[0]
    reason = f"ไม่มีเลขที่หายไป จึงใช้เลขที่พบน้อยสุดแทน: {prefix}"

triples = [prefix + p for p in pairs_final_5]

st.markdown('<div class="card"><div class="help">ข้อ 3 — เลขสามตัว (เติมเลขที่หายไปใน 5 งวดล่าสุดไว้หน้า)</div>'
            + " ".join([f'<span class="num mid">{t}</span>' for t in triples])
            + f'<div class="help" style="margin-top:.35rem;">ที่มา: {reason}</div>'
            + '</div>', unsafe_allow_html=True)

# ----------------------- STEP 4 -----------------------
# ข้อ 4: เลขสี่ตัว 1 ชุด = สุ่มเลือกหนึ่งชุดจากข้อ 3 แล้วเติม "หลักพัน" ของงวดล่าสุดไว้ด้านหน้า
random.seed(seed)
chosen_three = random.choice(triples) if triples else (prefix + single_pick + "0")
thousands = latest[0]   # หลักพันของงวดล่าสุด
four_final = thousands + chosen_three

st.markdown('<div class="card"><div class="help">ข้อ 4 — เลขสี่ตัว (สุ่มเลือก 1 ชุดจากข้อ 3 แล้วเติมหลักพันของงวดล่าสุด)</div>'
            f'<span class="num sm">{four_final}</span> '
            f'<span class="help">(หลักพันจากงวดล่าสุด {latest} ⇒ {thousands})</span>'
            '</div>', unsafe_allow_html=True)

# ----------------------- FOOTER -----------------------
st.caption("หมายเหตุ: เป็นฮิวริสติกเพื่อความสนุก ไม่รับประกันผลใด ๆ • © 2025 Lao Lotto")
