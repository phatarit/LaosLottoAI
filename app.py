# app.py
# -*- coding: utf-8 -*-
import random
import streamlit as st

st.set_page_config(
    page_title="Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด",
    page_icon="🇱🇦",
    layout="centered"
)

# ----------------- STYLE: ตัวเลขแดง พื้นขาว ชื่อสีน้ำเงิน -----------------
st.markdown("""
<style>
:root{
  --blue:#1f57c3;   /* น้ำเงิน */
  --red:#e0252a;    /* แดงตัวเลข */
}
.stApp { background:#f7f9ff; }
.block-container{ max-width:820px; }

.title {
  color: var(--blue);
  font-weight:800;
  font-size: 1.8rem;
  margin: 0.5rem 0 1rem 0;
  text-align:center;
}

/* กล่องแสดงผลแต่ละข้อ */
.card {
  background:#ffffff;
  border:3px solid var(--blue);
  border-radius:16px;
  padding:14px 16px;
  margin:10px 0 16px 0;
  box-shadow: 0 6px 18px rgba(0,0,0,0.07);
}

/* ป้ายหัวข้อ ข้อ 1-4 */
.tag {
  display:inline-block;
  background:var(--blue);
  color:#fff;
  padding:4px 12px;
  border-radius:999px;
  font-weight:700;
  letter-spacing:0.5px;
}

/* ตัวเลข */
.num-xl { color:var(--red); font-weight:900; font-size:3.2rem; line-height:1; }
.num-lg { color:var(--red); font-weight:900; font-size:2.4rem; line-height:1; }
.num-md { color:var(--red); font-weight:900; font-size:2.1rem; line-height:1; }
.num-sm { color:var(--red); font-weight:900; font-size:1.9rem; line-height:1; }

/* จัดชุดเลขแถวเดียวคั่นด้วยช่องไฟ */
.line { margin-top:8px; }
.bubble {
  display:inline-block; background:#fff; color:var(--red);
  border:2px solid var(--red); border-radius:12px;
  padding:4px 10px; margin:4px 6px 0 0; font-weight:900; font-size:1.4rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "เช่น\n8775\n3798\n6828\n0543\n0862"
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

# ----------------- LOGIC ตามกติกา -----------------
# งวดที่ 4 (index 3)
draw4 = draws[3]  # ตัวอย่าง: 0543
# ข้อ 1: สุ่ม 1 หลักจากเลขงวดที่ 4 → เด่น
digit_from_draw4 = random.choice(list(draw4))  # เช่น สุ่มจาก '0','5','4','3'

# ข้อ 2: ผสมกับเลขพิเศษ [4,5,6,2,1,0] แล้วสุ่ม 5 ชุด → เจาะ
specials = ['4','5','6','2','1','0']
pairs_all = [digit_from_draw4 + s for s in specials]
pairs_show = random.sample(pairs_all, k=min(5, len(pairs_all)))

# ข้อ 3: หาเลขที่ “หายไป” จาก 5 งวดล่าสุด (0-9)
seen = set("".join(draws))
missing = [str(d) for d in range(10) if str(d) not in seen]
if missing:
    prefix = random.choice(missing)     # สุ่มจากเลขที่หายไป
else:
    # ถ้าไม่มีเลขหายไป ให้ใช้เลขน้อยสุดตามค่าจริงแทน
    prefix = min(set(str(d) for d in range(10)), key=int)

triples = [prefix + p for p in pairs_show]  # เน้น (5 ชุด)

# ข้อ 4: สุ่มเลือกหนึ่งชุดจากข้อ 3 แล้วใส่หลักพันจาก “งวดก่อนหน้า” (งวดที่ 5)
draw5 = draws[4]
thousands_of_prev = draw5[0]            # หลักพันของงวดที่ 5
pick3 = random.choice(triples)
quad = thousands_of_prev + pick3        # รวย (1 ชุด)

# ----------------- OUTPUT (เฉพาะเลข/คำ) -----------------
# ข้อ 1 – เด่น (ใหญ่สุด)
st.markdown('<div class="card"><span class="tag">เด่น</span><div class="num-xl line">{}</div></div>'.format(digit_from_draw4), unsafe_allow_html=True)

# ข้อ 2 – เจาะ (รอง)
st.markdown('<div class="card"><span class="tag">เจาะ</span><div class="num-lg line">{}</div></div>'.format("  ".join(pairs_show)), unsafe_allow_html=True)

# ข้อ 3 – เน้น (รอง)
st.markdown('<div class="card"><span class="tag">เน้น</span><div class="num-md line">{}</div></div>'.format("  ".join(triples[:5])), unsafe_allow_html=True)

# ข้อ 4 – รวย (รอง)
st.markdown('<div class="card"><span class="tag">รวย</span><div class="num-sm line">{}</div></div>'.format(quad), unsafe_allow_html=True)
