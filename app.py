# app_v5.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict
import random

# ----------------- PAGE -----------------
st.set_page_config(
    page_title="Lao Lotto V.5",
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
.block-container{ max-width:960px; }
.title { color: var(--blue); font-weight:900; font-size: 1.9rem; line-height:1.1; }
.subtitle { color:#1f2937; margin-top:2px; font-size:0.98rem; }
.row { display:flex; gap:14px; align-items:center; flex-wrap:wrap; }
.card {
  background:#ffffff; border:3px solid var(--blue); border-radius:16px;
  padding:14px 16px; margin:10px 0 16px 0; box-shadow: 0 6px 18px rgba(0,0,0,0.07);
}
.heading { font-weight:900; font-size:1.1rem; color:#0f172a; margin-top:6px; }
.num-xl { color:var(--red); font-weight:900; font-size:2.6rem; display:flex; gap:18px; align-items:baseline; flex-wrap:wrap; }
.num-xl .label{ font-size:0.95rem; font-weight:800; color:#0f172a; background:#eef2ff; border:1px solid #c7d2fe; border-radius:8px; padding:2px 8px; }
.num-xl .digit{ font-size:3.1rem; font-weight:900; color:var(--red); margin-left:8px; }
.num-lg { color:var(--red); font-weight:900; font-size:2.1rem; line-height:1.2; }
.num-md { color:var(--red); font-weight:900; font-size:1.9rem; line-height:1.2; }
.num-sm { color:var(--red); font-weight:900; font-size:1.7rem; }
.badge { display:inline-block; padding:4px 10px; border:2px solid var(--red); border-radius:12px; margin:4px 8px 0 0; }
.footer { text-align:center; margin: 18px 0 8px 0; color:#475569; font-weight:700; }
hr{ border:none; border-top:1px dashed #cbd5e1; margin:6px 0 10px; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.5</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">กรุณาใส่เลข 4 ตัว 5 งวดล่าสุด</div>', unsafe_allow_html=True)

# ----------------- INPUTS -----------------
ph = "เช่น (เก่าสุด → ล่าสุด)\n8775\n3798\n6828\n0543\n0862"
raw = st.text_area("วางเลข 4 หลัก ทีละบรรทัด (ให้ครบ 5 งวด)", height=160, placeholder=ph)

left, right = st.columns([1,1])
with left:
    mode = st.selectbox("โหมดการแสดงผล", ["ครบตามเป้า", "คัด (สุ่มย่อชุด)"])
with right:
    seed = st.number_input("Seed สุ่ม (คัด)", min_value=0, max_value=999999, value=0, step=1)

draws = [s.strip() for s in raw.splitlines() if s.strip().isdigit() and len(s.strip()) == 4]
if len(draws) > 5:
    draws = draws[:5]

st.write(f"ข้อมูลที่อ่านได้: **{len(draws)} / 5** งวด")
if len(draws) < 5:
    st.stop()

if mode == "คัด (สุ่มย่อชุด)":
    random.seed(seed)

# ----------------- HELPERS -----------------
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

def multiset_key2(p):  # for 2-digit pairs ignoring order
    return tuple(sorted(p))

def multiset_key3(s):  # for 3-digit permutations ignoring order
    return tuple(sorted(s))

def build_singles(block):
    latest = block[-1]
    A = mod10_of(latest)
    B = int(latest[-1])
    M = mode_last_digit(block)
    cnt = freq_digits(block)
    last_digits = [int(s[-1]) for s in block]
    F = int(max(cnt.items(), key=lambda x: x[1])[0])
    T = sum(last_digits) % 10

    scores = defaultdict(float)
    for d in [A, B, F, T]:
        scores[d] += 1.0
    scores[A] += 0.6; scores[B] += 0.4; scores[F] += 0.8; scores[T] += 0.3
    for dstr, c in cnt.items(): scores[int(dstr)] += 0.05 * c

    # ครบตามเป้า: ต้อง 4 ตัวเพื่อ ≥80%
    ranked = [str(k) for k,_ in sorted(scores.items(), key=lambda x:(-x[1], x[0]))]
    info = {"A":A, "B":B, "M":M, "F":F, "T":T, "cnt":cnt}
    return ranked, info

def build_pairs(block, anchor_digit):
    latest = block[-1]
    A = mod10_of(latest); B = int(latest[-1])
    cnt = freq_digits(block)
    M = mode_last_digit(block)
    F = int(max(cnt.items(), key=lambda x: x[1])[0])

    w10=lambda x:(x+10)%10
    neighbors = [w10(B+k) for k in [-2, -1, 0, 1, 2]]
    topfreq = [int(d) for d,_ in cnt.most_common(3)]
    pool_digits = set([A, int(M), F] + neighbors + topfreq)

    fronts=[s[:2] for s in block]; backs=[s[-2:] for s in block]; last2=latest[-2:]
    pair_scores=defaultdict(float); cand=set()
    for d in pool_digits:
        cand.add(f"{anchor_digit}{d}")
        cand.add(f"{d}{anchor_digit}")
    for p in cand:
        a,b=int(p[0]),int(p[1])
        pair_scores[p]+=0.7*fronts.count(p)+0.9*backs.count(p)
        pair_scores[p]+=0.08*cnt.get(str(a),0)+0.08*cnt.get(str(b),0)
        hamming=(p[0]!=last2[0])+(p[1]!=last2[1])
        pair_scores[p]+={0:0.5,1:0.25,2:0.0}[hamming]
    # จัดอันดับและตัดกลับซ้ำ
    top_sorted=[p for p,_ in sorted(pair_scores.items(), key=lambda x:(-x[1], x[0]))]
    unique_pairs={}
    for p in top_sorted:
        key=multiset_key2(p)
        if key not in unique_pairs:
            unique_pairs[key]=p
    ranked_pairs=list(unique_pairs.values())
    return ranked_pairs, pair_scores

def build_triples_top(block, best_pair, info_cnt, k=22):
    # prefix pool: rare, A,B,M,F, topfreq(0..2)
    latest = block[-1]
    A = mod10_of(latest); B = int(latest[-1]); M = mode_last_digit(block)
    cnt = info_cnt
    rare = rare_digit_in(block)
    topfreq_digits = [d for d,_ in cnt.most_common(3)]
    prefix_pool = {rare, str(A), str(B), str(M)}
    prefix_pool |= set(str(d) for d in topfreq_digits)
    prefix_pool.add(str(int(max(cnt.items(), key=lambda x: x[1])[0])))  # F

    last3_latest = latest[-3:]
    hist_last3 = [d[-3:] for d in block[-5:]]
    hist_ms_count = Counter(multiset_key3(s) for s in hist_last3)

    def score_triple(t, best_pair_score=1.0):
        freq_sum = sum(cnt.get(ch,0) for ch in t)
        ca, cb = Counter(t), Counter(last3_latest)
        sim_last = sum(min(ca[d], cb[d]) for d in set(ca)|set(cb))
        ms = multiset_key3(t)
        hist_boost = hist_ms_count.get(ms,0)
        return 0.6*best_pair_score + 0.15*freq_sum + 0.15*sim_last + 0.1*hist_boost

    # ผู้ท้าชิงจาก prefix ทั้งหมด + best_pair
    candidates = [f"{p}{best_pair}" for p in sorted(prefix_pool)]
    uniq={}
    for t in candidates:
        key = multiset_key3(t)
        if key not in uniq:
            uniq[key]=t
    ranked = sorted(uniq.values(), key=lambda t:(-score_triple(t), t))[:k]
    return ranked

def build_quads(block, A):
    latest = block[-1]
    sims=lambda a,b: sum(x==y for x,y in zip(a,b))
    quads_all=[r[:-1]+str(A) for r in rotations(latest)]
    # ครบตามเป้า: ต้อง 36 ชุด → เพิ่มโดย permute digits ของ quads_all แบบมัลติเซ็ตไม่ซ้ำ
    uniq=set(quads_all)
    # สุ่มเติมจากการผสมตัวเลขบ่อย (ถ้าจำเป็น)
    # แต่เกณฑ์ขั้นต่ำ 36 จะทำด้วยการวน rot รูปแบบซ้ำแล้วซ้อนกันจนถึงจำนวน
    base=list(sorted(uniq, key=lambda q:(-sims(q, latest), q)))
    # เติมด้วยการเปลี่ยนหลักพันเป็นตัวเลขถี่สูงสุด เพื่อเพิ่มจำนวน
    if len(base) < 36:
        cnt = freq_digits(block)
        topd = [d for d,_ in cnt.most_common()]
        i=0
        while len(base) < 36 and i < len(topd)*5:
            for d in topd:
                q = str(d) + base[0][1:3] + str(A)
                if q not in base:
                    base.append(q)
                    if len(base) >= 36: break
            i+=1
    return base[:36]

# ----------------- BUILD -----------------
singles_ranked, info = build_singles(draws)
A, B, cnt = info["A"], info["B"], info["cnt"]

# ครบตามเป้า -> เดี่ยว 4 ตัว
singles_full = singles_ranked[:4]

# เลือก anchor จากเด่นสุด
anchor = singles_ranked[0]
pairs_ranked, pair_scores = build_pairs(draws, anchor)

# ครบตามเป้า -> 27 คู่ (ตัดกลับซ้ำแล้ว)
pairs_full = pairs_ranked[:27]

# เลือก best_pair สำหรับสร้างสามตัว
best_pair = pairs_ranked[0] if pairs_ranked else (singles_full[0] + singles_full[1])
triples_full = build_triples_top(draws, best_pair, cnt, k=22)

# สี่โต ครบตามเป้า 36 ชุด
quads_full = build_quads(draws, A)

# ----------------- FILTERED (คัด: สุ่มย่อชุด และ "สัมพันธ์กัน") -----------------
if mode == "คัด (สุ่มย่อชุด)":
    # เด่น/รอง อย่างละ 1
    if len(singles_ranked) < 2:
        singles_pick = singles_ranked + singles_ranked[:1]
    else:
        # สุ่ม 1 เด่นจาก Top-2, แล้วสุ่ม "รอง" ที่ต่างจากเด่นจาก Top-4
        top2 = singles_ranked[:2]
        top4 = singles_ranked[:4]
        d_main = random.choice(top2)
        rest = [x for x in top4 if x != d_main]
        d_sub = random.choice(rest) if rest else (top4[1] if len(top4)>1 else top4[0])
        singles_pick = [d_main, d_sub]

    # เน้น 5 ชุด: เลือกจาก pairs ที่ "มี" เด่นหรือรองเป็นหนึ่งในหลัก
    related_pairs = [p for p in pairs_ranked if (p[0] in singles_pick or p[1] in singles_pick)]
    pool_pairs = related_pairs if len(related_pairs) >= 5 else pairs_ranked
    pairs_pick = random.sample(pool_pairs, k=min(5, len(pool_pairs))) if len(pool_pairs) >= 5 else pool_pairs

    # เจาะลาก 5 ชุด: ใช้ best_pair ที่เกี่ยวข้องกับเด่น/รอง ถ้าเป็นไปได้
    try_best = next((p for p in pairs_ranked if (p[0] in singles_pick or p[1] in singles_pick)), best_pair)
    triples_pool = build_triples_top(draws, try_best, cnt, k=22)
    # กรองให้ "มีเลขร่วม" กับ (เด่น/รอง) หรือกับคู่ที่เลือก
    digit_rel = set("".join(singles_pick) + "".join(pairs_pick))
    triples_related = [t for t in triples_pool if any(ch in digit_rel for ch in t)]
    pool_triples = triples_related if len(triples_related) >= 5 else triples_pool
    if len(pool_triples) >= 5:
        triples_pick = random.sample(pool_triples, 5)
    else:
        triples_pick = pool_triples

    # สี่โต 1 ชุด: เอาจาก triple ใด triple หนึ่ง แล้วประกอบเป็น 4 หลัก + Fix หลักหน่วย = A
    if triples_pick:
        t = random.choice(triples_pick)
        # เลือกหลักพันจากเด่น/รอง หรือ rare
        rare = rare_digit_in(draws)
        lead_options = singles_pick + [rare, str(B)]
        lead = random.choice(lead_options)
        q = (lead + t)[:3] + str(A)   # ให้หลักหน่วย = A
        quad_pick = q
    else:
        quad_pick = (rotations(draws[-1])[0][:-1] + str(A))

else:
    # ครบตามเป้า
    singles_pick = singles_full
    pairs_pick   = pairs_full
    triples_pick = triples_full
    quad_pick    = quads_full[0] if quads_full else rotations(draws[-1])[0][:-1]+str(A)

# ----------------- OUTPUT -----------------
# 1) เด่น/รอง
if mode == "คัด (สุ่มย่อชุด)":
    st.markdown(f'''
    <div class="card">
      <div class="heading">เด่น / รอง (คัด)</div>
      <div class="num-xl">
        <span><span class="label">เด่น</span><span class="digit">{singles_pick[0]}</span></span>
        <span><span class="label">รอง</span><span class="digit">{singles_pick[1]}</span></span>
      </div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown(f'''
    <div class="card">
      <div class="heading">เด่น (ครบตามเป้า ≥80%) — 4 ตัว</div>
      <div class="num-xl">
        {" ".join([f"<span class='badge'>{d}</span>" for d in singles_pick])}
      </div>
    </div>
    ''', unsafe_allow_html=True)

# 2) เน้น
label2 = "เน้น (คัด 5 ชุด)" if mode == "คัด (สุ่มย่อชุด)" else "เน้น (ครบตามเป้า ≥50%) — 27 ชุด"
st.markdown(f'''
<div class="card">
  <div class="heading">{label2}</div>
  <div class="num-lg">{"  ".join(pairs_pick[:27])}</div>
</div>
''', unsafe_allow_html=True)

# 3) เจาะลาก
label3 = "เจาะลาก (คัด 5 ชุด)" if mode == "คัด (สุ่มย่อชุด)" else "เจาะลาก (ครบตามเป้า ≥10%) — 22 ชุด"
st.markdown(f'''
<div class="card">
  <div class="heading">{label3}</div>
  <div class="num-md">{"  ".join(triples_pick[:22])}</div>
</div>
''', unsafe_allow_html=True)

# 4) สี่โต
label4 = "สี่โต (คัด 1 ชุด)" if mode == "คัด (สุ่มย่อชุด)" else "สี่โต (ครบตามเป้า ≥5%) — 36 ชุด (แสดงตัวแรก)"
if mode == "คัด (สุ่มย่อชุด)":
    st.markdown(f'''
    <div class="card">
      <div class="heading">{label4}</div>
      <div class="num-sm">{quad_pick}</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown(f'''
    <div class="card">
      <div class="heading">{label4}</div>
      <div class="num-sm">{"  ".join(quads_full[:36])}</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025</div>', unsafe_allow_html=True)
