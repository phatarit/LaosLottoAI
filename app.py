# app_v4.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict

# ----------------- PAGE & THEME -----------------
st.set_page_config(
    page_title="Lao Lotto V.4",
    page_icon="icon.png",   # วาง icon.png ไว้โฟลเดอร์เดียวกับไฟล์นี้
    layout="centered"
)

# ----------------- STYLE -----------------
st.markdown("""
<style>
:root{
  --blue:#1f57c3;
  --red:#e0252a;
  --ink:#0f172a;
}
.stApp { background:#f7f9ff; }
.block-container{ max-width:900px; }
.title { color: var(--blue); font-weight:900; font-size: 1.9rem; line-height:1.1; }
.subtitle { color:#1f2937; margin-top:2px; font-size:0.98rem; }
.card {
  background:#ffffff; border:3px solid var(--blue); border-radius:16px;
  padding:14px 16px; margin:10px 0 16px 0; box-shadow: 0 6px 18px rgba(0,0,0,0.07);
}
.tag {
  display:inline-block; background:var(--blue); color:#fff;
  padding:4px 12px; border-radius:999px; font-weight:700; letter-spacing:0.5px;
}
.heading { font-weight:900; font-size:1.1rem; color:#0f172a; margin-top:6px; }
.num-xl { color:var(--red); font-weight:900; font-size:3.0rem; }
.num-lg { color:var(--red); font-weight:900; font-size:2.2rem; }
.num-md { color:var(--red); font-weight:900; font-size:2.0rem; }
.num-sm { color:var(--red); font-weight:900; font-size:1.7rem; }
.kbd{
  font-family:ui-monospace; background:#eef2ff; border:1px solid #c7d2fe;
  border-radius:6px; padding:2px 6px;
}
.note { font-size:0.92rem; color:#334155; margin-top:6px; }
.footer { text-align:center; margin: 18px 0 8px 0; color:#475569; font-weight:700; }
.warn { color:#b91c1c; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.4</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">กรุณาใส่เลข 4 ตัว 5 งวดล่าสุด</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "เช่น (เก่าสุด → ล่าสุด)\n8775\n3798\n6828\n0543\n0862"
raw = st.text_area("วางเลข 4 หลัก ทีละบรรทัด (ให้ครบ 5 งวด)", height=160, placeholder=ph)

# ดึงเฉพาะบรรทัดที่เป็นตัวเลข 4 หลัก
draws = [s.strip() for s in raw.splitlines() if s.strip().isdigit() and len(s.strip()) == 4]
if len(draws) > 5:
    draws = draws[:5]

st.write(f"ข้อมูลที่อ่านได้: **{len(draws)} / 5** งวด")
if len(draws) < 5:
    st.warning("กรุณาวางเลขให้ครบ 5 งวด (ตัวเลข 4 หลัก)")
    st.stop()

# ----------------- UTILITIES -----------------
def mod10_of(num4: str) -> int:
    return sum(int(c) for c in num4) % 10

def rotations(num4: str):
    # 4 แบบ: หมุน 0,1,2,3 ตำแหน่ง (ท้ายมาไว้หน้า)
    return [num4, num4[-1]+num4[:-1], num4[-2:]+num4[:-2], num4[-3:]+num4[:-3]]

def freq_digits(block):
    return Counter("".join(block))

def mode_last_digit(block):
    last = [s[-1] for s in block]
    cnt = Counter(last)
    m, _ = cnt.most_common(1)[0]
    return int(m)

def multiset_key3(s):  # คีย์มัลติเซ็ตของ 3 หลัก เช่น '397' -> ('7','9','3') sort
    return tuple(sorted(s))

def similarity_multiset3(a, b):  # นับจำนวนตัวที่ตรงในเชิงมัลติเซ็ต
    ca, cb = Counter(a), Counter(b)
    return sum(min(ca[d], cb[d]) for d in set(ca)|set(cb))

# ----------------- PREP -----------------
latest = draws[-1]
A = mod10_of(latest)          # mod10 ล่าสุด
B = int(latest[-1])           # หลักหน่วยล่าสุด
M = mode_last_digit(draws)    # โหมดของหลักหน่วย 5 งวด
digit_cnt = freq_digits(draws)
last_digits = [int(s[-1]) for s in draws]
F = int(max(digit_cnt.items(), key=lambda x: x[1])[0])  # เลขที่พบบ่อยสุดใน 5 งวด
T = sum(last_digits) % 10     # ผลรวมหลักหน่วยทั้ง 5 mod10

# ----------------- 1) เด่น — เลขเดี่ยว (Top-2) -----------------
single_scores = defaultdict(float)
for d in [A, B, F, T]:
    single_scores[d] += 1.0
single_scores[A] += 0.6
single_scores[B] += 0.4
single_scores[F] += 0.8
single_scores[T] += 0.3
for dstr, c in digit_cnt.items():
    single_scores[int(dstr)] += 0.05 * c

top2_single = sorted(single_scores.items(), key=lambda x: (-x[1], x[0]))[:2]
single_display = [str(k) for k, _ in top2_single]

# ----------------- 2) เน้น — เลขสองตัว (Anchor Top-8 | ตัดเลขสลับซ้ำ) -----------------
anchor_digit = str(top2_single[0][0])  # เลือกตัวที่คะแนนสูงกว่าเป็น anchor

def build_pairs_with_anchor_scored(block, anchor_digit: str):
    latest = block[-1]
    A = mod10_of(latest)
    B = int(latest[-1])
    cnt = freq_digits(block)
    M = mode_last_digit(block)
    F = int(max(cnt.items(), key=lambda x: x[1])[0])

    w10 = lambda x: (x+10) % 10
    neighbors = [w10(B+k) for k in [-2, -1, 0, 1, 2]]
    topfreq = [int(d) for d, _ in cnt.most_common(3)]
    pool_digits = set([A, int(M), F] + neighbors + topfreq)

    # candidate pairs: ต้องมี anchor อยู่ในคู่
    cand = set()
    for d in pool_digits:
        cand.add(f"{anchor_digit}{d}")
        cand.add(f"{d}{anchor_digit}")

    fronts = [s[:2] for s in block]
    backs  = [s[-2:] for s in block]
    last2  = latest[-2:]
    pair_scores = defaultdict(float)
    for p in cand:
        a, b = int(p[0]), int(p[1])
        pair_scores[p] += 0.7 * fronts.count(p) + 0.9 * backs.count(p)
        pair_scores[p] += 0.08 * cnt.get(str(a), 0) + 0.08 * cnt.get(str(b), 0)
        hamming = (p[0] != last2[0]) + (p[1] != last2[1])
        pair_scores[p] += {0: 0.5, 1: 0.25, 2: 0.0}[hamming]
    # Top-8 + remove reversed duplicates
    top_sorted = [p for p, _ in sorted(pair_scores.items(), key=lambda x: (-x[1], x[0]))]
    unique_pairs = {}
    for p in top_sorted:
        key = frozenset(p)
        if key not in unique_pairs:
            unique_pairs[key] = p
        if len(unique_pairs) == 8:
            break
    pairs8 = list(unique_pairs.values())
    return pairs8, pair_scores

pairs8, pair_scores = build_pairs_with_anchor_scored(draws, anchor_digit)
best_pair = pairs8[0] if pairs8 else f"{single_display[0]}{single_display[1]}"
best_pair_score = pair_scores.get(best_pair, 0.0)

# ----------------- 3) เจาะลาก — เลขสามตัว (Top-5 แบบให้คะแนน | ตัดสลับซ้ำ) -----------------
# สร้างผู้ท้าชิงจาก prefix แหล่งสำคัญ แล้ว "เลือก 5 อันดับแรก"
# แหล่ง prefix: rare (น้อยสุด), topfreq 0..2, A,B,M,F (รวม & unique)
def rare_digit_in(block):
    cnt = freq_digits(block)
    missing = [str(d) for d in range(10) if str(d) not in cnt]
    if missing:
        return missing[0]
    min_count = min(cnt[str(d)] for d in range(10))
    cands = [str(d) for d in range(10) if cnt[str(d)] == min_count]
    return sorted(cands, key=int)[0]

rare = rare_digit_in(draws)
topfreq_digits = [d for d, _ in digit_cnt.most_common(3)]
prefix_pool = {rare, str(A), str(B), str(M), str(F)} | set(topfreq_digits)
# จำกัดขนาดและเรียงตาม "น้อย → มาก" เพื่อกัน bias ตัวที่ถี่เกิน
prefix_sorted = sorted(prefix_pool, key=lambda d: (digit_cnt.get(d, 0), int(d)))
# เตรียมผู้ท้าชิง
triple_candidates = [f"{p}{best_pair}" for p in prefix_sorted]

# คะแนนของ "สามตัว"
# - พึ่งพาคะแนนคู่ฐาน (normalize)
# - บวกน้ำหนักความถี่ของตัวเลขทุกหลักใน triple
# - ความเหมือนกับ last3 ของงวดล่าสุด (มัลติเซ็ต)
# - บูสต์รูปแบบมัลติเซ็ตที่เคยโผล่ใน 10 งวดล่าสุด (last3)
last3_latest = latest[-3:]
hist_last3 = [d[-3:] for d in draws[-10:]]  # ใช้ 5 งวดที่ป้อนมีไม่พอ? ถ้าผู้ใช้ป้อนมากกว่า 5 ก็ยิ่งดี
hist_ms_count = Counter(multiset_key3(s) for s in hist_last3)

def score_triple(t: str) -> float:
    # ความถี่ของตัวเลขใน triple
    freq_sum = sum(digit_cnt.get(ch, 0) for ch in t)
    # ความเหมือนกับ last3 ล่าสุด (0..3)
    sim_last = similarity_multiset3(t, last3_latest)
    # บูสต์รูปแบบตามประวัติ
    ms = multiset_key3(t)
    hist_boost = hist_ms_count.get(ms, 0)
    # normalize / weights
    pscore = best_pair_score
    return 0.6*pscore + 0.15*freq_sum + 0.15*sim_last + 0.1*hist_boost

# ตัดสลับซ้ำ (permutation) แล้วคัด Top-5
unique_triples = {}
for t in triple_candidates:
    key = frozenset(t)
    if key not in unique_triples:
        unique_triples[key] = t
# ให้คะแนนและเลือก 5 อันดับ
ranked_triples = sorted(unique_triples.values(), key=lambda t: (-score_triple(t), t))[:5]

# ----------------- 4) สีโต — เลขสี่ตัว (Rotation + Fix หลักหน่วย = A) -> แสดงตัวเดียว -----------------
def sim(a, b): return sum(x == y for x, y in zip(a, b))
quads_all = [r[:-1] + str(A) for r in rotations(latest)]
quads_best = sorted(set(quads_all), key=lambda q: (-sim(q, latest), q))[0]

# ----------------- OUTPUT -----------------
st.markdown(f'''
<div class="card">
  <div class="heading">1) เด่น — เลขเดี่ยว (Top-2)</div>
  <div class="num-xl">{single_display[0]}  {single_display[1]}</div>
  <div class="note">A={A}, B={B}, F={F}, T={T}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <div class="heading">2) เน้น — เลขสองตัว (Anchor={anchor_digit}, Top-8 | ตัดเลขสลับซ้ำ)</div>
  <div class="num-lg">{"  ".join(pairs8)}</div>
  <div class="note">*สลับตำแหน่งเองได้ แต่ตัดชุดสลับซ้ำออกจากการแสดงผลแล้ว</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <div class="heading">3) เจาะลาก — เลขสามตัว (Top-5 | ระบบให้คะแนน | ตัดสลับซ้ำ)</div>
  <div class="num-md">{"  ".join(ranked_triples)}</div>
  <div class="note">เกณฑ์คัดเลือก: ความมั่นใจของคู่ฐาน + ความถี่เลข + ความเหมือนกับ 3 หลักท้ายล่าสุด + บูสต์รูปแบบใน 10 งวดหลัง</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <div class="heading">4) สีโต — เลขสี่ตัว (Rotation + Fix หลักหน่วย = A) <span class="kbd">แสดงตัวเดียว</span></div>
  <div class="num-sm">{quads_best}</div>
</div>
''', unsafe_allow_html=True)

st.markdown('<p class="note warn">คำเตือน: การทำนายนี้เป็นเชิงสถิติจากข้อมูลย้อนหลัง ไม่มีการรับประกันผลลัพธ์จริง</p>', unsafe_allow_html=True)

# ----------------- FOOTER -----------------
st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025</div>', unsafe_allow_html=True)
