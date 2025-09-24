# app_v3.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict
from pathlib import Path

# ----------------- PAGE & THEME -----------------
st.set_page_config(
    page_title="Lao Lotto V.3",
    page_icon="icon.png",  # ถ้ามีไฟล์ icon.png ในโฟลเดอร์เดียวกันจะถูกใช้
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
.num-xl { color:var(--red); font-weight:900; font-size:3.0rem; }
.num-lg { color:var(--red); font-weight:900; font-size:2.2rem; }
.num-md { color:var(--red); font-weight:900; font-size:2.0rem; }
.num-sm { color:var(--red); font-weight:900; font-size:1.7rem; }
.badge {
  display:inline-flex; align-items:center; gap:8px;
  background:#fff; color:var(--ink);
  border:2px solid var(--red); border-radius:12px;
  padding:6px 10px; margin:6px 8px 0 0; font-weight:800; font-size:1.2rem;
}
.badge small{ font-weight:700; font-size:0.75rem; color:#64748b; }
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
st.markdown('<div class="title">Lao Lotto V.3</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">กรุณาใส่เลข 4 ตัว 5 งวดล่าสุด</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "เช่น (เก่าสุด → ล่าสุด)\n8775\n3798\n6828\n0543\n0862"
raw = st.text_area("วางเลข 4 หลัก ทีละบรรทัด (ให้ครบ 5 งวด)", height=160, placeholder=ph)

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
    return [num4, num4[-1]+num4[:-1], num4[-2:]+num4[:-2], num4[-3:]+num4[:-3]]

def freq_digits(block):
    return Counter("".join(block))

def mode_last_digit(block):
    last = [s[-1] for s in block]
    cnt = Counter(last)
    m, _ = cnt.most_common(1)[0]
    return int(m)

# ----------------- PREP -----------------
latest = draws[-1]
A = mod10_of(latest)
B = int(latest[-1])
M = mode_last_digit(draws)
digit_cnt = freq_digits(draws)
last_digits = [int(s[-1]) for s in draws]
F = int(max(digit_cnt.items(), key=lambda x: x[1])[0])
T = sum(last_digits) % 10

# ----------------- SINGLE (Top-2) -----------------
single_scores = defaultdict(float)
for d in [A, B, F, T]:
    single_scores[d] += 1.0
single_scores[A] += 0.6; single_scores[B] += 0.4
single_scores[F] += 0.8; single_scores[T] += 0.3
for dstr, c in digit_cnt.items():
    single_scores[int(dstr)] += 0.05 * c
top2_single = sorted(single_scores.items(), key=lambda x: (-x[1], x[0]))[:2]
single_display = [str(k) for k, _ in top2_single]

# ----------------- 2-DIGIT (Anchor Top-8) -----------------
anchor_digit = str(top2_single[0][0])
def build_pairs_with_anchor_top8(block, anchor_digit: str):
    latest = block[-1]
    A = mod10_of(latest); B = int(latest[-1])
    cnt = freq_digits(block)
    M = mode_last_digit(block)
    F = int(max(cnt.items(), key=lambda x: x[1])[0])
    w10 = lambda x: (x+10) % 10
    neighbors = [w10(B+k) for k in [-2, -1, 0, 1, 2]]
    topfreq = [int(d) for d, _ in cnt.most_common(3)]
    pool_digits = set([A, int(M), F] + neighbors + topfreq)

    cand = set()
    for d in pool_digits:
        cand.add(f"{anchor_digit}{d}")
        cand.add(f"{d}{anchor_digit}")

    fronts = [s[:2] for s in block]; backs = [s[-2:] for s in block]
    last2 = latest[-2:]
    pair_scores = defaultdict(float)
    for p in cand:
        a, b = int(p[0]), int(p[1])
        pair_scores[p] += 0.7*fronts.count(p) + 0.9*backs.count(p)
        pair_scores[p] += 0.08*cnt.get(str(a),0) + 0.08*cnt.get(str(b),0)
        hamming = (p[0]!=last2[0]) + (p[1]!=last2[1])
        pair_scores[p] += {0:0.5,1:0.25,2:0.0}[hamming]
    top8 = [p for p, _ in sorted(pair_scores.items(), key=lambda x: (-x[1], x[0]))[:8]]
    return top8, pair_scores

pairs8, pair_scores = build_pairs_with_anchor_top8(draws, anchor_digit)

# ----------------- 3-DIGIT (Prefix 10 × Best Pair) -----------------
best_pair_for_triple = pairs8[0] if pairs8 else f"{single_display[0]}{single_display[1]}"
order = sorted(range(10), key=lambda d: (digit_cnt.get(str(d), 0), d))[:10]
prefixes10 = [str(d) for d in order]
triples_10 = [f"{p}{best_pair_for_triple}" for p in prefixes10]

# ----------------- 4-DIGIT (Rotations + Fix last=A) -----------------
def sim(a, b): return sum(x==y for x,y in zip(a,b))
quads_all = [r[:-1] + str(A) for r in rotations(latest)]
quads_sorted = sorted(set(quads_all), key=lambda q: (-sim(q, latest), q))[:5]

# ----------------- OUTPUT -----------------
st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 1: เลขเดี่ยว (Top-2)</span>
  <div class="num-xl">{single_display[0]}  {single_display[1]}</div>
  <div class="note">A={A}, B={B}, F={F}, T={T}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 2: เลขสองตัว (Anchor={anchor_digit}, Top-8)</span>
  <div class="num-lg">{"  ".join(pairs8)}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 3: เลขสามตัว (Prefix 10 × Best Pair)</span>
  <div class="num-md">{"  ".join(triples_10)}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <span class="tag">ข้อ 4: เลขสี่ตัว (Rotation+Fix)</span>
  <div class="num-sm">{"  ".join(quads_sorted)}</div>
</div>
''', unsafe_allow_html=True)

st.markdown('<p class="note warn">คำเตือน: การทำนายนี้เป็นเชิงสถิติจากข้อมูลย้อนหลัง ไม่มีการรับประกันผลลัพธ์จริง</p>', unsafe_allow_html=True)

# ----------------- FOOTER -----------------
st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025</div>', unsafe_allow_html=True)
