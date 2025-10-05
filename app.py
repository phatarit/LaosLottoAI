# app_v6.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict

st.set_page_config(
    page_title="Lao Lotto V.6",
    page_icon="🎯",
    layout="centered"
)

# ----------------- STYLE -----------------
st.markdown("""
<style>
:root{ --blue:#1f57c3; --red:#e0252a; --ink:#0f172a; }
.stApp { background:#f7f9ff; }
.block-container{ max-width:980px; }
.title { color: var(--blue); font-weight:900; font-size: 2rem; line-height:1.1; }
.subtitle { color:#1f2937; margin-top:4px; font-size:0.95rem; }
.card {
  background:#ffffff; border:3px solid var(--blue); border-radius:16px;
  padding:14px 16px; margin:12px 0 16px 0; box-shadow: 0 6px 18px rgba(0,0,0,0.07);
}
.heading { font-weight:900; font-size:1.1rem; color:#0f172a; margin-top:6px; }
.num-xl { color:var(--red); font-weight:900; font-size:2.6rem; display:flex; gap:18px; align-items:baseline; flex-wrap:wrap; }
.num-xl .label{ font-size:0.95rem; font-weight:800; color:#0f172a; background:#eef2ff; border:1px solid #c7d2fe; border-radius:8px; padding:2px 8px; }
.num-xl .digit{ font-size:3.1rem; font-weight:900; color:var(--red); margin-left:8px; }
.num-lg { color:var(--red); font-weight:900; font-size:2.05rem; line-height:1.25; }
.num-md { color:var(--red); font-weight:900; font-size:1.85rem; line-height:1.25; }
.num-sm { color:var(--red); font-weight:900; font-size:1.65rem; }
.tag { display:inline-block; padding:2px 8px; border-radius:10px; background:#eef2ff; border:1px solid #c7d2fe; color:#0f172a; font-weight:700; font-size:0.8rem; margin-left:8px;}
.badge { display:inline-block; padding:4px 10px; border:2px solid var(--red); border-radius:12px; margin:4px 8px 0 0; }
hr{ border:none; border-top:1px dashed #cbd5e1; margin:6px 0 10px; }
.footer { text-align:center; margin: 18px 0 8px 0; color:#475569; font-weight:700; }
.small { color:#475569; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.6 — Statistic-Driven Picks</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">วาง “เลข 4 หลัก” หลายงวด (สถิติจริงที่ออกแล้ว) — ระบบจะวิเคราะห์ทั้งชุดเพื่อหา เด่น/รอง, 2 ตัวคู่บน-ล่าง 5 ชุด (สลับตำแหน่งได้), 3 ตัวล่าง 5 ชุด และ 4 ตัวที่ประกอบจาก 3 ตัว</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = ("วางทีละบรรทัด (กี่งวดก็ได้ ≥ 20 จะยิ่งเสถียร)\n"
      "เช่น:\n9767\n5319\n1961\n4765\n2633\n...")

raw = st.text_area("วางผลย้อนหลัง (4 หลัก) ทีละบรรทัด", height=220, placeholder=ph)
rows = [s.strip() for s in raw.splitlines()]
draws = [s for s in rows if s.isdigit() and len(s) == 4]

st.write(f"อ่านข้อมูลได้ **{len(draws)}** งวด")
if len(draws) < 20:
    st.info("ใส่อย่างน้อย 20 งวด เพื่อความเสถียรของสถิติ.", icon="ℹ️")
    st.stop()

# ----------------- HELPERS -----------------
def multiset_key2(p):  # unordered pair key
    return tuple(sorted(p))

def multiset_key3(s):  # unordered triple key
    return tuple(sorted(s))

def normalize_scores(scores_dict):
    # min-max to [0,1] for display as "confidence"
    vals = list(scores_dict.values())
    lo, hi = min(vals), max(vals)
    if hi - lo == 0:
        return {k: 1.0 for k in scores_dict}
    return {k: (v - lo) / (hi - lo) for k, v in scores_dict.items()}

# ----------------- STATS -----------------
N = len(draws)
digits_all = "".join(draws)
cnt_digit_overall = Counter(digits_all)               # ทุกหลักรวมกัน
cnt_pos0 = Counter([d[0] for d in draws])             # หลักพัน
cnt_pos1 = Counter([d[1] for d in draws])             # หลักร้อย
cnt_pos2 = Counter([d[2] for d in draws])             # หลักสิบ
cnt_pos3 = Counter([d[3] for d in draws])             # หลักหน่วย (ล่าง)

# สถิติ 2 ตัว: หน้า (0-1), กลาง (1-2), ท้าย (2-3)
pairs_front = Counter([d[:2] for d in draws])
pairs_mid   = Counter([d[1:3] for d in draws])
pairs_back  = Counter([d[2:]  for d in draws])

# นับแบบ "ไม่สนลำดับ" สำหรับ last-2 (เพื่อรองรับ "สลับได้")
pairs_back_unordered = Counter([multiset_key2(d[2:]) for d in draws])

# สถิติ 3 ตัวท้าย
triples_back = Counter([d[1:] for d in draws])  # 3 ตัวท้าย (หลักร้อย-สิบ-หน่วย)
triples_tail = Counter([d[1:] for d in draws])  # alias (ใช้รวม scoring)

# ----------------- SCORING -----------------
# 1) เด่น/รอง (single digit)
#   - พิจารณา: overall freq, last-digit freq (pos3), และความถี่ใน "ตำแหน่งสิบ/หน่วย"
single_scores = defaultdict(float)
for d in "0123456789":
    f_all = cnt_digit_overall.get(d, 0) / (4*N)            # ทุกหลัก
    f_last = cnt_pos3.get(d, 0) / N                        # หลักหน่วย
    f_10   = cnt_pos2.get(d, 0) / N                        # หลักสิบ
    f_100  = cnt_pos1.get(d, 0) / N                        # หลักร้อย (เผื่อสำหรับ triple/quad)
    # น้ำหนักให้เน้นความเป็นไปได้ล่าง (last) และสองตัวล่าง
    score = 0.45*f_last + 0.35*f_10 + 0.15*f_all + 0.05*f_100
    single_scores[d] = score

# confidence (0..1) สำหรับแสดง
single_conf = normalize_scores(single_scores)
singles_ranked = sorted(single_scores.keys(), key=lambda x: (-single_scores[x], x))
main_digit, sub_digit = singles_ranked[0], singles_ranked[1]

# 2) สองตัวบน-ล่าง 5 ชุด (สลับตำแหน่งได้)
#   - สร้างจาก "เด่น/รอง" จับคู่กับตัวที่เกิดร่วมกันบ่อยในหลักสิบ-หน่วย
cooccur_with = Counter()
for d in draws:
    a, b = d[2], d[3]   # หลักสิบ-หน่วย
    cooccur_with[a] += 1
    cooccur_with[b] += 1

# pool: เด่น/รอง + top digits ที่เจอบ่อยในสิบ/หน่วย
top_tail_digits = [d for d, _ in Counter([x for d in draws for x in d[2:]]).most_common(6)]
pool_digits = list(dict.fromkeys([main_digit, sub_digit] + top_tail_digits))

pair_scores = {}
pair_seen_unordered = set()
cand_pairs = []
for a in pool_digits:
    for b in pool_digits:
        if a == b: 
            continue
        # คะแนนจากความถี่ในตำแหน่ง (2,3) ทั้งแบบตรงและสลับ
        score = 0.0
        score += 0.6 * (pairs_back.get(a+b, 0) + pairs_back.get(b+a, 0))
        # บูสต์ถ้ามีร่วมกับเด่น/รอง
        if a in (main_digit, sub_digit) or b in (main_digit, sub_digit):
            score += 0.4
        # บูสต์ตามความถี่ตัวเลขในสิบ/หน่วย
        score += 0.1 * (cnt_pos2.get(a,0)+cnt_pos3.get(b,0)+cnt_pos2.get(b,0)+cnt_pos3.get(a,0))/max(N,1)
        key_u = multiset_key2(a+b)
        if key_u not in pair_seen_unordered:
            pair_seen_unordered.add(key_u)
            cand_pairs.append((a+b, score))

cand_pairs = sorted(cand_pairs, key=lambda x:(-x[1], x[0]))[:5]
pairs5 = [p for p,_ in cand_pairs]

# 3) สามตัวล่าง 5 ชุด
#   - ใช้ “สองตัวล่างที่คัดได้” แล้วเติมอีก 1 ตัวที่มีแนวโน้ม (เน้นหลักร้อยกับเด่น/รอง)
triple_scores = {}
for p in pairs5:
    a, b = p[0], p[1]  # สิบ-หน่วยตามลำดับ
    # ตัวเลือกหลักร้อยจาก: เด่น, รอง, top หลักร้อยจริง
    top_pos1_digits = [d for d,_ in cnt_pos1.most_common(6)]
    choices = list(dict.fromkeys([main_digit, sub_digit] + top_pos1_digits))
    for h in choices:
        t = h + a + b
        # คะแนน: สถิติ 3 ตัวท้าย, ความถี่หลักร้อยจริง, บูสต์ถ้ามีเด่น/รองปน
        score = 0.6*triples_tail.get(t,0) + 0.25*cnt_pos1.get(h,0)
        if h in (main_digit, sub_digit): score += 0.25
        triple_scores[t] = max(triple_scores.get(t,0), score)

triples5 = [t for t,_ in sorted(triple_scores.items(), key=lambda x:(-x[1], x[0]))[:5]]

# 4) สี่ตัว จาก “สามตัวที่คัด” 1 ชุด แล้วใส่ “ตัวใดก็ได้” ที่หลักพัน
#   - เลือกสามตัวที่คะแนนสูงสุด แล้วเติมหลักพันจากเด่น/รอง/หรือ top หลักพัน
quad_candidates = []
if triples5:
    t = triples5[0]  # ตัวท็อป
    top_pos0_digits = [d for d,_ in cnt_pos0.most_common(5)]
    lead_pool = list(dict.fromkeys([main_digit, sub_digit] + top_pos0_digits))
    for L in lead_pool:
        quad_candidates.append(L + t)

# เลือก 1 ชุดที่คะแนนดีที่สุดตามสถิติจริง (นับความถี่ 4 หลัก)
cnt_full = Counter(draws)
quad_pick = max(quad_candidates, key=lambda q: cnt_full.get(q,0)) if quad_candidates else (singles_ranked[0] + triples5[0] if triples5 else "")

# ----------------- OUTPUT -----------------
# เด่น / รอง
st.markdown("""
<div class="card">
  <div class="heading">เด่น / รอง (จากสถิติทั้งหมด)</div>
  <div class="num-xl">
""", unsafe_allow_html=True)
st.markdown(
    f"<span><span class='label'>เด่น</span><span class='digit'>{main_digit}</span>"
    f"<span class='tag'>conf ~ {single_conf[main_digit]*100:.0f}%</span></span>  "
    f"<span><span class='label'>รอง</span><span class='digit'>{sub_digit}</span>"
    f"<span class='tag'>conf ~ {single_conf[sub_digit]*100:.0f}%</span></span>",
    unsafe_allow_html=True
)
st.markdown("</div></div>", unsafe_allow_html=True)

# 2 ตัว (บน-ล่างสลับได้) 5 ชุด
st.markdown("""
<div class="card">
  <div class="heading">สองตัวคู่ (บน-ล่างสลับได้) — 5 ชุด</div>
  <div class="small">หมายเหตุ: คัดจากสถิติหลักสิบ-หน่วยทั้งหมด โดยบูสต์ชุดที่เกี่ยวข้องกับ “เด่น/รอง”</div>
  <div class="num-lg">
""", unsafe_allow_html=True)
st.markdown("  ".join([f"{p} / {p[1]}{p[0]}" for p in pairs5]), unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# 3 ตัวล่าง 5 ชุด
st.markdown("""
<div class="card">
  <div class="heading">สามตัวล่าง — 5 ชุด (ประกอบจากคู่สองตัวที่คัด + หลักร้อยที่เป็นไปได้)</div>
  <div class="num-md">
""", unsafe_allow_html=True)
st.markdown("  ".join(triples5) if triples5 else "-", unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# 4 ตัว (จากสามตัวที่คัด + ใส่หลักพัน)
st.markdown("""
<div class="card">
  <div class="heading">สี่ตัว (ประกอบจากสามตัวที่คัด + ใส่หลักพันจาก เด่น/รอง/สถิติหลักพัน)</div>
  <div class="num-sm">
""", unsafe_allow_html=True)
st.markdown(quad_pick if quad_pick else "-", unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# สรุปสถิติเพิ่มเติม (อธิบายที่มาแบบย่อ)
with st.expander("ดูรายละเอียดสถิติที่ใช้คำนวณ / วิธีคิด (โปร่งใส)"):
    st.markdown(f"""
- งวดทั้งหมดที่ใช้วิเคราะห์: **{N}**  
- ความถี่หลักหน่วย (Top 5): {", ".join([f"{d}:{cnt_pos3[d]}" for d,_ in cnt_pos3.most_common(5)])}  
- ความถี่หลักสิบ (Top 5): {", ".join([f"{d}:{cnt_pos2[d]}" for d,_ in cnt_pos2.most_common(5)])}  
- ความถี่หลักร้อย (Top 5): {", ".join([f"{d}:{cnt_pos1[d]}" for d,_ in cnt_pos1.most_common(5)])}  
- ความถี่หลักพัน (Top 5): {", ".join([f"{d}:{cnt_pos0[d]}" for d,_ in cnt_pos0.most_common(5)])}  

**สูตรเด่น/รอง:** 0.45×freq(หลักหน่วย) + 0.35×freq(หลักสิบ) + 0.15×freq(ทุกหลักรวม) + 0.05×freq(หลักร้อย)  
**สองตัว:** เน้น last-2 ทั้งแบบตรงและสลับ + บูสต์ถ้ามีเด่น/รองร่วม  
**สามตัวล่าง:** ต่อยอดจากคู่สองตัว แล้วเลือกหลักร้อยจาก (เด่น/รอง/Top หลักร้อย) โดยอิงสถิติ 3 ตัวท้าย  
**สี่ตัว:** ใช้สามตัวที่ดีที่สุด แล้วใส่หลักพันจาก (เด่น/รอง/Top หลักพัน)  
    """)

st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025</div>', unsafe_allow_html=True)
