# app_v7.2_hybrid.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict
import math
import numpy as np

st.set_page_config(page_title="Lao Lotto V.7.2", page_icon="🎯", layout="centered")

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
.heading { font-weight:900; font-size:1.25rem; color:#0f172a; margin:8px 0 12px; }
.num-xl { color:var(--red); font-weight:900; font-size:4.2rem; display:flex; gap:40px; align-items:baseline; flex-wrap:wrap; justify-content:center;}
.num-xl .label{ font-size:1.4rem; font-weight:800; color:#0f172a; background:#eef2ff; border:2px solid #c7d2fe; border-radius:12px; padding:6px 14px; }
.num-xl .digit{ font-size:4.8rem; font-weight:900; color:var(--red); margin-left:12px; }
.num-lg { font-weight:900; font-size:2.6rem; line-height:1.25; }
.num-md { font-weight:900; font-size:2.2rem; line-height:1.25; }
.num-sm { font-weight:900; font-size:2.0rem; }
.tag { display:inline-block; padding:4px 12px; border-radius:12px; background:#eef2ff; border:1px solid #c7d2fe; color:#0f172a; font-weight:700; font-size:1.0rem; margin-left:12px;}
.badge { display:inline-flex; align-items:baseline; gap:10px; padding:6px 12px; border:2px solid var(--red); border-radius:14px; margin:6px 10px 0 0; }
.perc { font-size:1.0rem; color:#0f172a; background:#fff; border:1px dashed #c7d2fe; padding:2px 8px; border-radius:10px; }
.footer { text-align:center; margin: 18px 0 8px 0; color:#475569; font-weight:700; }
.digit-red { color: var(--red) !important; font-weight:900; }
.tip { display:inline-block; margin-top:6px; padding:6px 10px; background:#fff7ed; border:1px solid #fdba74; color:#7c2d12; border-radius:10px; font-weight:700; }
.small { color:#475569; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.7.2 — Hybrid & Calibrated</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Hybrid pool (conditional odds/PMI) · Isotonic calibration · Anti-bias penalty · Custom 4-digit rule</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "กรุณาวาง 'งวดล่าสุด 10 งวด' (4 หลัก/บรรทัด) เช่น 9767\\n5319\\n1961 ..."
st.markdown("<span class='tip'>คำชี้แจง: กรุณาลงงวดล่าสุด 10 งวด (ระบบจะใช้เฉพาะ 10 งวดท้ายสุด)</span>", unsafe_allow_html=True)
raw = st.text_area("ผลย้อนหลัง (ใช้เฉพาะ 10 งวดล่าสุดจากรายการที่วาง)", height=260, placeholder=ph)

# อ่านข้อมูล
all_draws = [s.strip() for s in raw.splitlines() if s.strip().isdigit() and len(s.strip())==4]
st.write(f"อ่านข้อมูลได้ทั้งหมด **{len(all_draws)}** งวด")
if len(all_draws) < 10:
    st.info("กรุณาวางอย่างน้อย 10 งวดล่าสุด (ระบบจะใช้เฉพาะ 10 งวดท้ายสุดอัตโนมัติ).", icon="ℹ️")
    st.stop()

# ใช้เฉพาะ 10 งวดล่าสุด
draws = all_draws[-10:]
st.write("กำลังวิเคราะห์ **10 งวดล่าสุด** จากรายการที่วางมา ✅")
N = len(draws)
recent5 = draws[-5:] if N >= 5 else draws

# ----------------- HELPERS -----------------
def pct(x):
    try:
        return f"{x*100:.1f}%"
    except:
        return "—"

def safe_div(a,b,eps=1e-9): return a/ b if b>0 else 0.0

def normalize_scores(sc):
    v=list(sc.values()); lo,hi=min(v),max(v)
    return {k:(v_ - lo)/(hi-lo) if hi>lo else 1.0 for k,v_ in sc.items()}

def sigmoid(x):
    try:
        return 1.0/(1.0+math.exp(-x))
    except OverflowError:
        return 0.0 if x<-50 else 1.0

def quantile_bins(xs, qs):
    xs_np=np.array(xs)
    edges=np.quantile(xs_np, qs)
    # ensure strictly increasing
    for i in range(1,len(edges)):
        if edges[i]<=edges[i-1]:
            edges[i]=edges[i-1]+1e-8
    idxs=np.searchsorted(edges, xs_np, side="right")  # 0..len(qs)
    return edges, idxs

def isotonic_from_bins(scores, labels, n_bins=10):
    """
    Quantile-binning -> empirical rate per bin -> isotonic (cumulative max) -> piecewise-linear map
    Fallback: temperature-style logistic if sample is too small.
    """
    if len(scores) != len(labels) or len(scores) < max(12, n_bins):
        # fallback: soft logistic scaling based on min-max normalized score
        s = np.array(scores, dtype=float)
        s = (s - s.min())/(s.max()-s.min()+1e-12)
        T = 1.5  # temperature (>1 makes softer)
        return lambda x: sigmoid(( (x - s.min())/(s.max()-s.min()+1e-12) - 0.5 )*4.0/T)

    qs = np.linspace(0.1,0.9,n_bins-1)  # internal cut points
    edges, idxs = quantile_bins(scores, qs)
    K = n_bins
    bin_scores = [[] for _ in range(K)]
    bin_labels = [[] for _ in range(K)]
    for s,y,i in zip(scores,labels,idxs):
        bin_scores[i].append(s); bin_labels[i].append(y)
    # center & rate
    centers=[]; rates=[]
    for k in range(K):
        if bin_scores[k]:
            centers.append(float(np.mean(bin_scores[k])))
            rates.append(float(np.mean(bin_labels[k])))
        else:
            centers.append(0.0); rates.append(0.0)
    # isotonicization (non-decreasing)
    iso_rates=[]
    cur=-1.0
    for r in rates:
        cur=max(cur, r)
        iso_rates.append(cur)
    # keep inside (0,1)
    iso_rates=[min(max(r,1e-6),1-1e-6) for r in iso_rates]
    # sort by centers
    pairs=sorted(zip(centers,iso_rates))
    xs=[p[0] for p in pairs]; ys=[p[1] for p in pairs]
    def cal_fn(x):
        if x<=xs[0]: return ys[0]
        if x>=xs[-1]: return ys[-1]
        import bisect
        i=bisect.bisect_right(xs, x)
        x0,x1=xs[i-1], xs[i]
        y0,y1=ys[i-1], ys[i]
        t=safe_div(x-x0, x1-x0)
        return y0*(1-t)+y1*t
    return cal_fn

# ----------------- STATS -----------------
cnt_pos=[Counter([d[i] for d in draws]) for i in range(4)]   # pos 0..3
pairs_back=Counter([d[2:] for d in draws])                   # AB
triples_tail=Counter([d[1:] for d in draws])                 # HAB
full4=Counter(draws)
cnt_overall=Counter("".join(draws))
def p_pos(d,pos): return safe_div(cnt_pos[pos].get(d,0), N)

# recent-5 stats for H (หลักร้อย)
cnt_pos_recent5 = [Counter([d[i] for d in recent5]) for i in range(4)]

# ----------------- CONDITIONAL / PMI for Hybrid pool -----------------
digits="0123456789"
eps=1e-3  # smoothing
# base marginals at A (pos2) and B (pos3)
pA={a: p_pos(a,2) for a in digits}
pB={b: p_pos(b,3) for b in digits}
# joints p(ab) from pairs_back (empirical)
pAB={}
for a in digits:
    for b in digits:
        key=a+b
        pAB[key]=safe_div(pairs_back.get(key,0), N)

# conditional odds matrices
condB_givenA = {(a,b): (pairs_back.get(a+b,0)+eps) / (cnt_pos[2].get(a,0)+10*eps) for a in digits for b in digits}
condA_givenB = {(a,b): (pairs_back.get(a+b,0)+eps) / (cnt_pos[3].get(b,0)+10*eps) for a in digits for b in digits}

# PMI for pair (scale: log)
PMI={(a+b): math.log( safe_div(pAB[a+b]+eps, (pA[a]+eps)*(pB[b]+eps) ) ) for a in digits for b in digits}

# ----------------- SMOOTHED PROBS -----------------
L2,L3,L4,ALPHA=0.85,0.80,0.80,0.70

def p_pair_smooth(a,b):
    return L2*(pAB[a+b]) + (1-L2)*(pA[a]*pB[b])

def p_triple_smooth(h,a,b):
    p_emp= safe_div(triples_tail.get(h+a+b,0), N)
    p_back= ALPHA*p_pos(h,1)*p_pair_smooth(a,b) + (1-ALPHA)*p_pos(h,1)*p_pos(a,2)*p_pos(b,3)
    return L3*p_emp + (1-L3)*p_back

def p_quad_smooth(L,h,a,b):
    p_emp = safe_div(full4.get(L+h+a+b,0), N)
    return L4*p_emp + (1-L4)*p_pos(L,0)*p_triple_smooth(h,a,b)

# ----------------- PENALTIES -----------------
last = draws[-1]             # งวดล่าสุด
last_AB = last[2:]
last_H = last[1]

G_pair_freq = 0.15  # หักคะแนนคู่ที่ถี่มาก
G_hit_last = 0.08   # หักถ้าชนงวดล่าสุด
G_same_digit = 0.04 # หัก a==b
def apply_pair_penalty(a,b, raw):
    penalty = 0.0
    f = pAB[a+b]
    penalty += G_pair_freq * (f**2)
    if (a+b)==last_AB: penalty += G_hit_last
    if a==b: penalty += G_same_digit
    return max(raw - penalty, 0.0)

def apply_triple_penalty(h,a,b, raw):
    penalty = 0.0
    if h==last_H and (a+b)==last_AB:
        penalty += 0.10
    penalty += 0.07 * (pAB[a+b]**2)
    return max(raw - penalty, 0.0)

# ----------------- CALIBRATION DATASET (in-sample) -----------------
# pairs
pair_scores=[]; pair_labels=[]
for a in digits:
    for b in digits:
        s = p_pair_smooth(a,b)
        s = apply_pair_penalty(a,b,s)
        pair_scores.append(s)
        pair_labels.append(1 if pairs_back.get(a+b,0)>0 else 0)
cal_pair = isotonic_from_bins(pair_scores, pair_labels, n_bins=10)

# triples
triple_scores=[]; triple_labels=[]
for h in digits:
    for a in digits:
        for b in digits:
            s = p_triple_smooth(h,a,b)
            s = apply_triple_penalty(h,a,b,s)
            triple_scores.append(s)
            triple_labels.append(1 if triples_tail.get(h+a+b,0)>0 else 0)
cal_triple = isotonic_from_bins(triple_scores, triple_labels, n_bins=12)

# quads (positives + sampled negatives)
quad_scores=[]; quad_labels=[]
for q,c in full4.items():  # positives
    L,H,A,B = q[0],q[1],q[2],q[3]
    s = p_quad_smooth(L,H,A,B)
    quad_scores.append(s); quad_labels.append(1)
rng = np.random.default_rng(42)  # negatives
neg_samples=200
for _ in range(neg_samples):
    L = rng.integers(0,10); H = rng.integers(0,10); A = rng.integers(0,10); B = rng.integers(0,10)
    L,H,A,B = str(L),str(H),str(A),str(B)
    if full4.get(L+H+A+B,0)>0:
        continue
    s = p_quad_smooth(L,H,A,B)
    quad_scores.append(s); quad_labels.append(0)
cal_quad = isotonic_from_bins(quad_scores, quad_labels, n_bins=12)

# ----------------- HYBRID POOL (A,B,H,L) -----------------
def rank_AB_candidates(kA=8, kB=8):
    scoreA=defaultdict(float); scoreB=defaultdict(float)
    for d in digits:
        scoreA[d] += 0.55*p_pos(d,2) + 0.10*(cnt_overall[d]/(4*N))
        scoreB[d] += 0.55*p_pos(d,3) + 0.10*(cnt_overall[d]/(4*N))
    for a in digits:
        scoreA[a] += 0.25*max(condB_givenA[(a,b)] for b in digits)
        scoreA[a] += 0.10*max(PMI[a+b] for b in digits)
    for b in digits:
        scoreB[b] += 0.25*max(condA_givenB[(a,b)] for a in digits)
        scoreB[b] += 0.10*max(PMI[a+b] for a in digits)
    A_pool = [k for k,_ in sorted(scoreA.items(), key=lambda x:(-x[1], x[0]))][:kA]
    B_pool = [k for k,_ in sorted(scoreB.items(), key=lambda x:(-x[1], x[0]))][:kB]
    return A_pool, B_pool, scoreA, scoreB

def rank_H_candidates(kH=8):
    scoreH=defaultdict(float)
    for h in digits:
        scoreH[h] = 0.80*p_pos(h,1) + 0.20*(cnt_overall[h]/(4*N))
    H_pool = [k for k,_ in sorted(scoreH.items(), key=lambda x:(-x[1], x[0]))][:kH]
    return H_pool, scoreH

A_pool, B_pool, scoreA, scoreB = rank_AB_candidates()
H_pool, scoreH = rank_H_candidates()

# ----------------- MAIN CALC -----------------
# เด่น/รอง (เพิ่ม hybrid term เล็กน้อย)
sc=defaultdict(float)
for d in digits:
    sc[d]=0.45*p_pos(d,3)+0.35*p_pos(d,2)+0.10*(cnt_overall[d]/(4*N))+0.05*p_pos(d,1)+0.05*max(0.0,scoreB[d]-scoreA[d])
rank_digits=sorted(sc,key=lambda x:(-sc[x],x)); main,sub=rank_digits[0],rank_digits[1]
conf=normalize_scores(sc)

# 2 ตัวท้าย — hybrid + penalties + calibration
pairs=[]
for a in A_pool:
    for b in B_pool:
        # ถ้าต้องการห้าม A==B ให้เปิดบรรทัดต่อไป
        # if a==b: continue
        raw = p_pair_smooth(a,b)
        raw = apply_pair_penalty(a,b, raw)
        score = raw + 0.05*condB_givenA[(a,b)] + 0.03*max(0.0, PMI[a+b])
        pairs.append((a+b, score))
tmp=defaultdict(float)
for k,v in pairs:
    tmp[k]=max(tmp[k], v)
pairs = [(k,tmp[k]) for k in tmp]
pairs.sort(key=lambda x:(-x[1], x[0]))
pairs = pairs[:5]
pairs_cal = [(p, cal_pair(s)) for p,s in pairs]

# 3 ตัวท้าย — ต่อ H จาก H_pool แล้วใช้ penalty + calibration
triples=[]
if pairs:
    triple_scores={}
    for pair_key, _ in pairs:
        a,b = pair_key[0], pair_key[1]
        for h in H_pool:
            raw = p_triple_smooth(h,a,b)
            raw = apply_triple_penalty(h,a,b, raw)
            raw += 0.03*(condB_givenA[(a,b)] + condA_givenB[(a,b)])
            t = h+a+b
            triple_scores[t]=max(triple_scores.get(t,0.0), raw)
    triples = sorted(triple_scores.items(), key=lambda x:(-x[1], x[0]))[:5]
    triples_cal = [(t, cal_triple(s)) for t,s in triples]
else:
    triples=[]; triples_cal=[]

# 4 ตัวเต็ม — กฎใหม่: L = หลักพันของงวดล่าสุด, H = น้อยที่สุดใน 5 งวดล่าสุด
L_fixed = last[0]
h_counts_recent = cnt_pos_recent5[1]
min_c = min(h_counts_recent.get(d,0) for d in digits)
H_least = [d for d in digits if h_counts_recent.get(d,0)==min_c]

quad="-"; qp_raw=0.0; qp_cal=0.0
if pairs and H_least:
    P = [p for p,_ in pairs[:3]]  # ใช้ top-3 pairs
    qlist=[]
    for p in P:
        a,b = p[0], p[1]
        for h in H_least:
            raw = p_quad_smooth(L_fixed, h, a, b)
            if h_counts_recent.get(h,0)==0:
                raw += 0.02  # โบนัสเล็กน้อยหาก "ไม่เคยเกิด" ใน recent5
            q = L_fixed + h + a + b
            qlist.append((q, raw))
    if qlist:
        qlist.sort(key=lambda x:(-x[1], x[0]))
        quad, qp_raw = qlist[0]
        qp_cal = cal_quad(qp_raw)

# ----------------- OUTPUT -----------------
st.markdown(f"""
<div class="card">
  <div class="heading">เด่น / รอง (เน้นหลักสิบ-หน่วย · Hybrid)</div>
  <div class="num-xl">
    <span><span class="label">เด่น</span><span class="digit digit-red">{main}</span>
    <span class="tag">conf ~ {conf[main]*100:.0f}%</span></span>
    <span><span class="label">รอง</span><span class="digit digit-red">{sub}</span>
    <span class="tag">conf ~ {conf[sub]*100:.0f}%</span></span>
  </div>
  <div class="small">* conf คือคะแนน normalize ภายใน 0–100 ของ 10 ตัวเลข (ไม่ใช่โอกาสรวม 100%)</div>
</div>
""", unsafe_allow_html=True)

# 2 ตัว
pairs_html = "  ".join([
    f"<span class='badge'><span class='digit-red'>{p}</span><span class='perc'>{pct(s_cal)}</span></span>"
    for p, s_cal in pairs_cal
]) if pairs_cal else "<span class='perc'>ไม่พอข้อมูลคัด 2 ตัว</span>"
st.markdown(f"<div class='card'><div class='heading'>สองตัวคู่ (Hybrid + Calibrated) — 5 ชุด</div><div class='num-lg'>{pairs_html}</div></div>", unsafe_allow_html=True)

# 3 ตัว
triples_html = "  ".join([
    f"<span class='badge'><span class='digit-red'>{t}</span><span class='perc'>{pct(s_cal)}</span></span>"
    for t, s_cal in triples_cal
]) if triples_cal else "<span class='perc'>ยังคัดไม่ได้ (ข้อมูลไม่พอ)</span>"
st.markdown(f"<div class='card'><div class='heading'>สามตัวล่าง (Hybrid + Calibrated) — 5 ชุด</div><div class='num-md'>{triples_html}</div></div>", unsafe_allow_html=True)

# 4 ตัว
quad_html = (f"<span class='badge'><span class='digit-red'>{quad}</span><span class='perc'>{pct(qp_cal)}</span></span>"
             if quad != "-" else "<span class='perc'>ยังคัดไม่ได้</span>")
hleast_txt = ", ".join(H_least) if H_least else "-"
st.markdown(f"<div class='card'><div class='heading'>สี่ตัว (กฎกำหนด L และ H · Calibrated)</div><div class='num-sm'>{quad_html}</div><div class='small'>กฎ: L = หลักพันงวดล่าสุด ({L_fixed}) · H = น้อยที่สุดใน 5 งวดล่าสุด ({hleast_txt})</div></div>", unsafe_allow_html=True)

st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025 · V7.2</div>', unsafe_allow_html=True)
