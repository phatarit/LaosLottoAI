# app_v7.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict

st.set_page_config(
    page_title="Lao Lotto V.7",
    page_icon="🎯",
    layout="centered"
)

# ----------------- STYLE -----------------
st.markdown("""
<style>
:root{ --blue:#1f57c3; --red:#e0252a; --ink:#0f172a; }
.stApp { background:#f7f9ff; }
.block-container{ max-width:1024px; }
.title { color: var(--blue); font-weight:900; font-size: 2.2rem; line-height:1.1; }
.subtitle { color:#1f2937; margin-top:6px; font-size:1.0rem; }
.card {
  background:#ffffff; border:3px solid var(--blue); border-radius:18px;
  padding:18px 20px; margin:14px 0 18px 0; box-shadow: 0 8px 22px rgba(0,0,0,0.08);
}
.heading { font-weight:900; font-size:1.2rem; color:#0f172a; margin:6px 0 10px; }
.num-xl { color:var(--red); font-weight:900; font-size:3.2rem; display:flex; gap:24px; align-items:baseline; flex-wrap:wrap; }
.num-xl .label{ font-size:1.05rem; font-weight:800; color:#0f172a; background:#eef2ff; border:1px solid #c7d2fe; border-radius:10px; padding:4px 10px; }
.num-xl .digit{ font-size:3.6rem; font-weight:900; color:var(--red); margin-left:8px; }
.num-lg { font-weight:900; font-size:2.6rem; line-height:1.25; }
.num-md { font-weight:900; font-size:2.2rem; line-height:1.25; }
.num-sm { font-weight:900; font-size:2.0rem; }
.tag { display:inline-block; padding:3px 10px; border-radius:12px; background:#eef2ff; border:1px solid #c7d2fe; color:#0f172a; font-weight:700; font-size:0.9rem; margin-left:10px;}
.badge { display:inline-flex; align-items:baseline; gap:10px; padding:6px 12px; border:2px solid var(--red); border-radius:14px; margin:6px 10px 0 0; }
.perc { font-size:1.0rem; color:#0f172a; background:#fff; border:1px dashed #c7d2fe; padding:2px 8px; border-radius:10px; }
hr{ border:none; border-top:1px dashed #cbd5e1; margin:8px 0 12px; }
.footer { text-align:center; margin: 18px 0 8px 0; color:#475569; font-weight:700; }
.small { color:#475569; font-size:0.95rem; }

/* สีแดงเข้มให้ตัวเลขผลลัพธ์ทุกที่ */
.digit-red { color: var(--red) !important; font-weight:900; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.7 — Smoothed Probabilities</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">วางผล 4 หลัก ย้อนหลัง (หลายงวดยิ่งแม่น) → คัด เด่น/รอง, 2 ตัว (ไม่สลับ), 3 ตัวล่าง และ 4 ตัว พร้อมเปอร์เซ็นต์โอกาสจากสถิติจริง + smoothing/back-off</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = ("วางทีละบรรทัด (อย่างน้อย 20 งวดแนะนำ)\n"
      "เช่น:\n9767\n5319\n1961\n4765\n2633\n...")
raw = st.text_area("วางผลย้อนหลัง (4 หลัก) ทีละบรรทัด", height=260, placeholder=ph)
rows = [s.strip() for s in raw.splitlines()]
draws = [s for s in rows if s.isdigit() and len(s) == 4]

st.write(f"อ่านข้อมูลได้ **{len(draws)}** งวด")
if len(draws) < 20:
    st.info("ใส่อย่างน้อย 20 งวด เพื่อความเสถียรของเปอร์เซ็นต์.", icon="ℹ️")
    st.stop()

# ----------------- HELPERS -----------------
def normalize_scores(scores_dict):
    vals = list(scores_dict.values())
    lo, hi = min(vals), max(vals)
    if hi - lo == 0:
        return {k: 1.0 for k in scores_dict}
    return {k: (v - lo) / (hi - lo) for k, v in scores_dict.items()}

def pct(x):  # to percentage string
    return f"{x*100:.1f}%"

# ----------------- STATS -----------------
N = len(draws)
digits_all = "".join(draws)

# ความถี่รายหลัก
cnt_pos = [Counter([d[i] for d in draws]) for i in range(4)]
cnt_overall = Counter(digits_all)

# สถิติ 2 ตัวท้าย (สิบ-หน่วย) แบบลำดับ
pairs_back = Counter([d[2:] for d in draws])

# สถิติ 3 ตัวท้าย (ร้อย-สิบ-หน่วย)
triples_tail = Counter([d[1:] for d in draws])

# สถิติครบ 4 ตัว
full4 = Counter(draws)

# ความน่าจะเป็นเชิงประจักษ์ของ “เลขที่ตำแหน่ง”
def p_pos(digit, pos):
    return cnt_pos[pos].get(digit, 0) / N

# ----------------- SMOOTHED PROBS -----------------
# พารามิเตอร์ smoothing (ปรับเพื่อให้เปอร์เซ็นต์ดูเสถียรและเน้นสถิติจริง)
LAMBDA2 = 0.85   # 2 ตัว
LAMBDA3 = 0.80   # 3 ตัว
LAMBDA4 = 0.80   # 4 ตัว
ALPHA   = 0.70   # น้ำหนักให้ dependency ระหว่าง (สิบ-หน่วย)

def prob_pair_last2(a, b):
    # empirical
    p_emp = pairs_back.get(a+b, 0) / N
    # back-off: independent at positions
    p_ind = p_pos(a,2) * p_pos(b,3)
    return LAMBDA2 * p_emp + (1 - LAMBDA2) * p_ind

def prob_triple_tail(h, a, b):
    p_emp = triples_tail.get(h+a+b, 0) / N
    p_pair = prob_pair_last2(a, b)
    p_back = ALPHA * (p_pos(h,1) * p_pair) + (1 - ALPHA) * (p_pos(h,1) * p_pos(a,2) * p_pos(b,3))
    return LAMBDA3 * p_emp + (1 - LAMBDA3) * p_back

def prob_quad(L, h, a, b):
    p_emp = full4.get(L+h+a+b, 0) / N
    p_back = p_pos(L,0) * prob_triple_tail(h, a, b)
    return LAMBDA4 * p_emp + (1 - LAMBDA4) * p_back

# ----------------- RANKING LOGIC -----------------
# เด่น/รอง: เน้นหลักหน่วย/หลักสิบ (ล่าง) มากที่สุด
single_scores = defaultdict(float)
for d in "0123456789":
    score = 0.50*p_pos(d,3) + 0.35*p_pos(d,2) + 0.10*(cnt_overall.get(d,0)/(4*N)) + 0.05*p_pos(d,1)
    single_scores[d] = score
singles_ranked = sorted(single_scores.keys(), key=lambda x: (-single_scores[x], x))
main_digit, sub_digit = singles_ranked[0], singles_ranked[1]
single_conf = normalize_scores(single_scores)

# 2 ตัวท้าย 5 ชุด (ไม่แสดงสลับ)
# พูลตัวเลข: เด่น/รอง + top ของหลักสิบ-หน่วย
top_tail_digits = [d for d, _ in Counter([x for d in draws for x in d[2:]]).most_common(8)]
pool_digits = list(dict.fromkeys([main_digit, sub_digit] + top_tail_digits))

pair_candidates = []
seen = set()
for a in pool_digits:
    for b in pool_digits:
        if a == b: 
            continue
        key = a+b
        if key in seen: 
            continue
        seen.add(key)
        pair_candidates.append((key, prob_pair_last2(a,b)))

pair_candidates.sort(key=lambda x: (-x[1], x[0]))
pairs5 = pair_candidates[:5]

# 3 ตัวล่าง 5 ชุด: ต่อจากคู่ 2 ตัว + เติมหลักร้อย (เด่น/รอง + top หลักร้อย)
triple_candidates = {}
top_pos1 = [d for d,_ in cnt_pos[1].most_common(8)]
choices_h = list(dict.fromkeys([main_digit, sub_digit] + top_pos1))
for key, _p in pairs5:
    a, b = key[0], key[1]
    for h in choices_h:
        t = h+a+b
        triple_candidates[t] = prob_triple_tail(h, a, b)

triples5 = sorted(triple_candidates.items(), key=lambda x: (-x[1], x[0]))[:5]

# 4 ตัว: ใช้ทริปเปิลอันดับ 1 แล้วเติมหลักพัน (เด่น/รอง + top หลักพัน)
quad_pick, quad_prob = "-", 0.0
if triples5:
    best_triple = triples5[0][0]  # h a b
    h, a, b = best_triple[0], best_triple[1], best_triple[2]
    top_pos0 = [d for d,_ in cnt_pos[0].most_common(6)]
    lead_pool = list(dict.fromkeys([main_digit, sub_digit] + top_pos0))
    quad_list = []
    for L in lead_pool:
        q = L + h + a + b
        quad_list.append((q, prob_quad(L, h, a, b)))
    quad_list.sort(key=lambda x: (-x[1], x[0]))
    if quad_list:
        quad_pick, quad_prob = quad_list[0]

# ----------------- OUTPUT -----------------
# เด่น / รอง
st.markdown("""
<div class="card">
  <div class="heading">เด่น / รอง (ถ่วงน้ำหนักหลักสิบ-หน่วย)</div>
  <div class="num-xl">
""", unsafe_allow_html=True)
st.markdown(
    f"<span><span class='label'>เด่น</span>"
    f"<span class='digit digit-red'>{main_digit}</span>"
    f"<span class='tag'>conf ~ {single_conf[main_digit]*100:.0f}%</span></span>"
    f"  <span><span class='label'>รอง</span>"
    f"<span class='digit digit-red'>{sub_digit}</span>"
    f"<span class='tag'>conf ~ {single_conf[sub_digit]*100:.0f}%</span></span>",
    unsafe_allow_html=True
)
st.markdown("</div></div>", unsafe_allow_html=True)

# 2 ตัว (ไม่สลับ) + % โอกาส
pairs_html = "  ".join([
    f"<span class='badge'><span class='digit-red'>{p}</span>"
    f"<span class='perc'>{pct(prob)}</span></span>"
    for p, prob in pairs5
])
st.markdown(f"""
<div class="card">
  <div class="heading">สองตัวคู่ (บน-ล่าง ไม่สลับ) — 5 ชุด</div>
  <div class="num-lg">{pairs_html}</div>
</div>
""", unsafe_allow_html=True)

# 3 ตัวล่าง + % โอกาส
triples_html = "  ".join([
    f"<span class='badge'><span class='digit-red'>{t}</span>"
    f"<span class='perc'>{pct(prob)}</span></span>"
    for t, prob in triples5
]) if triples5 else "-"
st.markdown(f"""
<div class="card">
  <div class="heading">สามตัวล่าง — 5 ชุด</div>
  <div class="num-md">{triples_html}</div>
</div>
""", unsafe_allow_html=True)

# 4 ตัว + % โอกาส
quad_html = (f"<span class='badge'><span class='digit-red'>{quad_pick}</span>"
             f"<span class='perc'>{pct(quad_prob)}</span></span>") if quad_pick != "-" else "-"
st.markdown(f"""
<div class="card">
  <div class="heading">สี่ตัว (จากสามตัวอันดับ 1 + หลักพันที่เป็นไปได้)</div>
  <div class="num-sm">{quad_html}</div>
</div>
""", unsafe_allow_html=True)

# อธิบายสั้น ๆ
with st.expander("ดูวิธีคิดเปอร์เซ็นต์ (smoothing/back-off)"):
    st.markdown(f"""
- งวดที่ใช้วิเคราะห์: **{N}**  
- สูตรโดยสรุป  
  - **2 ตัว (สิบ-หน่วย)**:  \\(\\hat p= \\lambda_2\\,\\texttt{{freq}}/N + (1-\\lambda_2)\\,P(สิบ)P(หน่วย)\\), ที่นี่ \\(\\lambda_2={LAMBDA2}\\)  
  - **3 ตัว (ร้อย-สิบ-หน่วย)**:  \\(\\hat p= \\lambda_3\\,\\texttt{{freq}}/N + (1-\\lambda_3)\\,[\\alpha\\,P(ร้อย)\\,\\hat p_{{2ตัว}} + (1-\\alpha)\\,P(ร้อย)P(สิบ)P(หน่วย)]\\), โดย \\(\\lambda_3={LAMBDA3},\\ \\alpha={ALPHA}\\)  
  - **4 ตัว (พัน-ร้อย-สิบ-หน่วย)**:  \\(\\hat p= \\lambda_4\\,\\texttt{{freq}}/N + (1-\\lambda_4)\\,P(พัน)\\,\\hat p_{{3ตัว}}\\), โดย \\(\\lambda_4={LAMBDA4}\\)  
- เด่น/รอง: ถ่วงน้ำหนัก **หลักหน่วย 50% + หลักสิบ 35%** + (รวม/หลักร้อย) 15% เพื่อเน้นล่าง
- ระบบคัด **Top-k ตามเปอร์เซ็นต์ที่สูงที่สุด** ในแต่ละหมวด
    """)

st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025</div>', unsafe_allow_html=True)
