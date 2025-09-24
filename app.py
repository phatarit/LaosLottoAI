# app.py
# -*- coding: utf-8 -*-
import random
import streamlit as st

# ── Config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด",
    page_icon="🇱🇦",
    layout="centered"
)

# ── Theme (พื้นขาว ตัวแดง กรอบน้ำเงิน) ─────────────────────────────
st.markdown("""
<style>
:root{
  --blue:#0E5BD8; --red:#E02424; --light:#ffffff; --muted:#182949;
}
.stApp { background: var(--light); color: #111; }
.block-container { max-width: 860px; padding-top: 1rem; }

.app-title{ color: var(--blue); font-weight: 800; margin: 0 0 .5rem 0; }

.card{ border:2px solid var(--blue); border-radius:16px; padding:14px; margin:.75rem 0; background:#fff; }
.section{ border:2px solid var(--blue); border-radius:14px; padding:12px 14px; margin:.5rem 0; }

.badge{ font-weight:700; color:var(--blue); margin-right:.5rem; }

.num-big   { color:var(--red); font-size:3.0rem; line-height:1; font-weight:800; letter-spacing:.04em; }
.num-large { color:var(--red); font-size:2.2rem; line-height:1.1; font-weight:800; letter-spacing:.03em; }
.num-md    { color:var(--red); font-size:1.8rem; line-height:1.1; font-weight:800; letter-spacing:.03em; }
.num-sm    { color:var(--red); font-size:1.6rem; line-height:1.1; font-weight:800; letter-spacing:.02em; }

.grid{ display:grid; grid-template-columns: 1fr; gap:10px; }
.item{ display:flex; align-items:center; justify-content:space-between; }

.chips{ display:flex; flex-wrap:wrap; gap:8px; }
.chip{ border:2px solid var(--blue); border-radius:12px; padding:6px 10px; background:#fff; }
.chip > span{ color:var(--red); font-weight:800; font-size:1.4rem; letter-spacing:.02em; }

h1,h2,h3,h4 { margin:0; padding:0; }
textarea, .stTextArea textarea { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
</style>
""", unsafe_allow_html=True)

# ── Title ────────────────────────────────────────────────────────────
st.markdown('<h1 class="app-title">Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด</h1>', unsafe_allow_html=True)

# ── Input ────────────────────────────────────────────────────────────
example = "6828\n0543\n0862\n9252\n1222"
raw = st.text_area("วางเลข 4 หลัก (ทีละบรรทัด 5 งวด)", value=example, height=140)
lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

def valid_4d(s): return len(s)==4 and s.isdigit()

if len(lines) != 5 or not all(valid_4d(x) for x in lines):
    st.info("กรุณาวางเลข **4 หลัก** ให้ครบ **5 งวด** (เช่นตัวอย่างด้านบน) แล้วผลลัพธ์จะแสดงด้านล่าง")
    st.stop()

# จัดลำดับให้บรรทัดบนสุด = งวดที่ 1 (เก่าสุด), บรรทัดล่างสุด = งวดล่าสุด
draws = lines[:]           # ['6828','0543','0862','9252','1222']
first = draws[0]           # งวดที่ 1
last  = draws[-1]          # งวดล่าสุด
prev3 = draws[-4:-1]       # 3 งวดก่อนหน้า (ไม่นับงวดล่าสุด)

# ── Step 1: เด่น ────────────────────────────────────────────────────
# เลขเดี่ยว = หลักสิบ + หลักหน่วย ของงวดที่ 1
lead_digits = [first[2], first[3]]  # tens, ones
lead_digits = list(dict.fromkeys(lead_digits))  # unique, keep order  (เช่น ['2','8'])

# ── Step 2: เจาะ ────────────────────────────────────────────────────
# คู่จากเลขเดี่ยว × เลขที่ "พบใน 3 งวดก่อนหน้า" โดยคัดเฉพาะเลขพิเศษ {4,5,6,2,1,0} และแสดง 5 ชุด
special = ['4','5','6','2','1','0']
seen_prev3 = set(''.join(prev3))  # ตัวเลขที่พบใน 3 งวดก่อนหน้า
partners = [d for d in special if d in seen_prev3]  # รักษาลำดับจาก special

def pick_pairs(lead: str, partners_list, k=5):
    pairs = [lead + p for p in partners_list]
    return pairs[:k]

pairs_by_lead = {d: pick_pairs(d, partners, 5) for d in lead_digits}

# ── Step 3: เน้น ────────────────────────────────────────────────────
# หาเลข "ที่หายไป" จาก 5 งวดล่าสุด; ถ้าไม่มี ให้ใช้ตัวที่พบน้อยสุดแทน
seen_5 = set(''.join(draws))
missing = [str(i) for i in range(10) if str(i) not in seen_5]
if missing:
    prefix = sorted(missing, key=lambda x:int(x))[0]
else:
    # เลือกตัวที่พบน้อยสุดใน 5 งวด
    from collections import Counter
    cnt = Counter(''.join(draws))
    m = min(cnt.values())
    prefix = sorted([d for d,c in cnt.items() if c==m], key=lambda x:int(x))[0]

triples_by_lead = {
    d: [prefix + p for p in pairs_by_lead[d]]
    for d in lead_digits
}

# ── Step 4: รวย ─────────────────────────────────────────────────────
# สุ่มเลือกหนึ่งชุดจาก "เน้น" แล้วเอาหลักพันของงวดล่าสุดมาใส่หน้า
random.seed()  # ใช้ระบบสุ่มปกติ
all_triples = [t for lst in triples_by_lead.values() for t in lst]
chosen3 = random.choice(all_triples) if all_triples else prefix + (lead_digits[0] if lead_digits else '0') + '0'
thousands = last[0]  # หลักพันของงวดล่าสุด
rich4 = thousands + chosen3  # 4 หลัก 1 ชุด

# ── Render (ในกรอบเดียวกัน, ตัวแดง, ป้ายสีน้ำเงิน) ───────────────
st.markdown('<div class="card">', unsafe_allow_html=True)

# เด่น
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<span class="badge">เด่น</span>', unsafe_allow_html=True)
st.markdown(f'<div class="num-big">{" ".join(lead_digits)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# เจาะ (เลขสองตัว 5 ชุด ต่อหนึ่งเลขเด่น)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<span class="badge">เจาะ</span>', unsafe_allow_html=True)
for d in lead_digits:
    pairs = pairs_by_lead.get(d, [])
    if pairs:
        st.markdown(f'<div class="num-large">{"  ".join(pairs)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# เน้น (เลขสามตัว: ใส่เลขที่หายไปไว้หน้า)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<span class="badge">เน้น</span>', unsafe_allow_html=True)
for d in lead_digits:
    tris = triples_by_lead.get(d, [])
    if tris:
        st.markdown(f'<div class="num-md">{"  ".join(tris)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# รวย (เลขสี่ตัว 1 ชุด)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<span class="badge">รวย</span>', unsafe_allow_html=True)
st.markdown(f'<div class="num-sm">{rich4}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
