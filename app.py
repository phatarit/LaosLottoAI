# app_v4.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict

# ----------------- PAGE -----------------
st.set_page_config(
    page_title="Lao Lotto V.4",
    page_icon="icon.png",
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
.heading { font-weight:900; font-size:1.1rem; color:#0f172a; margin-top:6px; }
.num-xl { color:var(--red); font-weight:900; font-size:2.6rem; display:flex; gap:18px; align-items:baseline; flex-wrap:wrap; }
.num-xl .label{ font-size:0.95rem; font-weight:800; color:#0f172a; background:#eef2ff; border:1px solid #c7d2fe; border-radius:8px; padding:2px 8px; }
.num-xl .digit{ font-size:3.1rem; font-weight:900; color:var(--red); margin-left:8px; }
.num-lg { color:var(--red); font-weight:900; font-size:2.2rem; }
.num-md { color:var(--red); font-weight:900; font-size:2.0rem; }
.num-sm { color:var(--red); font-weight:900; font-size:1.7rem; }
.footer { text-align:center; margin: 18px 0 8px 0; color:#475569; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.4</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">กรุณาใส่เลข 4 ตัว 5 งวดล่าสุด</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "เช่น (เก่าสุด → ล่าสุด)\n8775\n3798\n6828\n0543\n0862"
raw = st.text_area("วางเลข 4 หลัก ทีละบรรทัด (ให้ครบ 5 งวด)", height=160, placeholder=ph)

draws = [s.strip() for s in raw.splitlines() if s.strip().isdigit() and len(s.strip()) == 4]
if len(draws) > 5:
    draws = draws[:5]

st.write(f"ข้อมูลที่อ่านได้: **{len(draws)} / 5** งวด")
if len(draws) < 5:
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
    return int(cnt.most_common(1)[0][0])

def rare_digit_in(block):
    cnt = freq_digits(block)
    missing = [str(d) for d in range(10) if str(d) not in cnt]
    if missing:
        return missing[0]
    min_count = min(cnt[str(d)] for d in range(10))
    cands = [str(d) for d in range(10) if cnt[str(d)] == min_count]
    return sorted(cands, key=int)[0]

def multiset_key3(s): return tuple(sorted(s))
def similarity_multiset3(a,b):
    ca,cb=Counter(a),Counter(b)
    return sum(min(ca[d],cb[d]) for d in set(ca)|set(cb))

# ----------------- PREP -----------------
latest = draws[-1]
A = mod10_of(latest)
B = int(latest[-1])
M = mode_last_digit(draws)
digit_cnt = freq_digits(draws)
last_digits = [int(s[-1]) for s in draws]
F = int(max(digit_cnt.items(), key=lambda x: x[1])[0])
T = sum(last_digits) % 10

# ----------------- 1) เด่น/รอง — เลขเดี่ยว Top-2 -----------------
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
anchor_digit = str(top2_single[0][0])

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

# ----------------- 3) เจาะลาก — เลขสามตัว (Top-5 | ตัดสลับซ้ำ) -----------------
rare = rare_digit_in(draws)
topfreq_digits = [d for d, _ in digit_cnt.most_common(3)]
prefix_pool = {rare, str(A), str(B), str(M), str(F)} | set(topfreq_digits)
prefix_sorted = sorted(prefix_pool, key=lambda d: (digit_cnt.get(d, 0), int(d)))
triple_candidates = [f"{p}{best_pair}" for p in prefix_sorted]

last3_latest = latest[-3:]
hist_last3 = [d[-3:] for d in draws[-5:]]
hist_ms_count = Counter(multiset_key3(s) for s in hist_last3)

def score_triple(t: str) -> float:
    freq_sum = sum(digit_cnt.get(ch, 0) for ch in t)
    sim_last = similarity_multiset3(t, last3_latest)
    ms = multiset_key3(t)
    hist_boost = hist_ms_count.get(ms, 0)
    return 0.6*best_pair_score + 0.15*freq_sum + 0.15*sim_last + 0.1*hist_boost

uniq_triples = {}
for t in triple_candidates:
    key = frozenset(t)
    if key not in uniq_triples:
        uniq_triples[key] = t
triples_5 = sorted(uniq_triples.values(), key=lambda t: (-score_triple(t), t))[:5]

# ----------------- 4) สี่โต — เลขสี่ตัว (Rotation + Fix หลักหน่วย = A) -> แสดงตัวเดียว -----------------
def sim(a, b): return sum(x == y for x, y in zip(a, b))
quads_all = [r[:-1] + str(A) for r in rotations(latest)]
quad_best = sorted(set(quads_all), key=lambda q: (-sim(q, latest), q))[0]

# ----------------- OUTPUT -----------------
st.markdown(f'''
<div class="card">
  <div class="heading">เด่น / รอง</div>
  <div class="num-xl">
    <span><span class="label">เด่น</span><span class="digit">{single_display[0]}</span></span>
    <span><span class="label">รอง</span><span class="digit">{single_display[1]}</span></span>
  </div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <div class="heading">เน้น</div>
  <div class="num-lg">{"  ".join(pairs8)}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <div class="heading">เจาะลาก</div>
  <div class="num-md">{"  ".join(triples_5)}</div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="card">
  <div class="heading">สี่โต</div>
  <div class="num-sm">{quad_best}</div>
</div>
''', unsafe_allow_html=True)

st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025</div>', unsafe_allow_html=True)
