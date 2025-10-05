# app_v7.1_10only.py
# -*- coding: utf-8 -*-
import streamlit as st
from collections import Counter, defaultdict

st.set_page_config(page_title="Lao Lotto V.7.1", page_icon="🎯", layout="centered")

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

/* ขยาย "เด่น/รอง" ให้ใหญ่ขึ้นชัดเจน */
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

/* ตัวเลขแดงทั้งหมด */
.digit-red { color: var(--red) !important; font-weight:900; }
.tip { display:inline-block; margin-top:6px; padding:6px 10px; background:#fff7ed; border:1px solid #fdba74; color:#7c2d12; border-radius:10px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Lao Lotto V.7.1 — Smoothed Probabilities</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">ระบบวิเคราะห์จากสถิติจริง (Smoothing / Back-off) พร้อมเปอร์เซ็นต์ความน่าจะเป็น</div>', unsafe_allow_html=True)

# ----------------- INPUT -----------------
ph = "กรุณาวาง 'งวดล่าสุด 10 งวด' (4 หลัก/บรรทัด) เช่น 9767\\n5319\\n1961 ..."
st.markdown("<span class='tip'>คำชี้แจง: กรุณาลงงวดล่าสุด 10 งวด</span>", unsafe_allow_html=True)
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

# ----------------- HELPERS -----------------
def pct(x): return f"{x*100:.1f}%"
def normalize_scores(sc):
    v=list(sc.values()); lo,hi=min(v),max(v)
    return {k:(v_ - lo)/(hi-lo) if hi>lo else 1 for k,v_ in sc.items()}

# ----------------- STATS -----------------
N=len(draws)
cnt_pos=[Counter([d[i] for d in draws]) for i in range(4)]   # pos 0..3
pairs_back=Counter([d[2:] for d in draws])                   # AB
triples_tail=Counter([d[1:] for d in draws])                 # HAB
full4=Counter(draws)
cnt_overall=Counter("".join(draws))
def p_pos(d,pos): return cnt_pos[pos].get(d,0)/N

# ----------------- SMOOTHED PROBS -----------------
# (Default) หากต้องการ Hybrid ให้ค่อยอัปเกรดเป็น v7.2 ภายหลังได้
L2,L3,L4,ALPHA=0.85,0.80,0.80,0.70
def p_pair(a,b):
    # 2 ตัวท้าย (สิบ-หน่วย) แบบ smoothing
    return L2*(pairs_back.get(a+b,0)/N) + (1-L2)*(p_pos(a,2)*p_pos(b,3))
def p_triple(h,a,b):
    # 3 ตัวท้าย (ร้อย-สิบ-หน่วย) แบบ smoothing + back-off
    p_emp=triples_tail.get(h+a+b,0)/N
    p_back=ALPHA*p_pos(h,1)*p_pair(a,b) + (1-ALPHA)*p_pos(h,1)*p_pos(a,2)*p_pos(b,3)
    return L3*p_emp + (1-L3)*p_back
def p_quad(L,h,a,b):
    # 4 ตัวเต็ม
    return L4*(full4.get(L+h+a+b,0)/N) + (1-L4)*p_pos(L,0)*p_triple(h,a,b)

# ----------------- MAIN CALC -----------------
# เด่น/รอง (ถ่วงน้ำหนักหลักสิบ-หน่วย)
sc=defaultdict(float)
for d in "0123456789":
    sc[d]=0.5*p_pos(d,3)+0.35*p_pos(d,2)+0.1*(cnt_overall[d]/(4*N))+0.05*p_pos(d,1)
rank=sorted(sc,key=lambda x:(-sc[x],x)); main,sub=rank[0],rank[1]
conf=normalize_scores(sc)

# 2 ตัว (บน-ล่าง ไม่สลับ) — คัด 5 ชุด
top_tail=[d for d,_ in Counter([x for d in draws for x in d[2:]]).most_common(8)]
pool=list(dict.fromkeys([main,sub]+top_tail))
pairs=[(a+b,p_pair(a,b)) for a in pool for b in pool if a!=b]
pairs.sort(key=lambda x:(-x[1],x[0]))
pairs=pairs[:5]

# 3 ตัวล่าง — คัด 5 ชุด
triples=[]
if pairs:
    top_h=[d for d,_ in cnt_pos[1].most_common(8)]
    H=list(dict.fromkeys([main,sub]+top_h))
    triple_scores={}
    for pair_key, _prob in pairs:
        a,b = pair_key[0], pair_key[1]
        for h in H:
            t = h+a+b
            triple_scores[t] = p_triple(h,a,b)
    triples = sorted(triple_scores.items(), key=lambda x:(-x[1], x[0]))[:5]

# 4 ตัว — เลือกจากสามตัวอันดับ 1 + หลักพัน (main/sub/top)
quad="-"; qp=0.0
if triples:
    best_triple = triples[0][0]    # string 'hab'
    h,a,b = best_triple[0], best_triple[1], best_triple[2]
    top_L=[d for d,_ in cnt_pos[0].most_common(6)]
    Ls=list(dict.fromkeys([main,sub]+top_L))
    qlist=[(L+h+a+b,p_quad(L,h,a,b)) for L in Ls]
    qlist.sort(key=lambda x:(-x[1],x[0]))
    quad, qp = qlist[0]
elif pairs:
    # เผื่อกรณี triples ว่าง: สร้าง 4 ตัวจากคู่บนสุด + เด่นเป็นหลักร้อย/พัน
    a,b = pairs[0][0][0], pairs[0][0][1]
    h_candidates = list(dict.fromkeys([main,sub] + [d for d,_ in cnt_pos[1].most_common(4)]))
    L_candidates = list(dict.fromkeys([main,sub] + [d for d,_ in cnt_pos[0].most_common(4)]))
    best_q = "-"
    best_p = 0.0
    for h in h_candidates:
        for L in L_candidates:
            q = L+h+a+b
            p = p_quad(L,h,a,b)
            if p > best_p:
                best_q, best_p = q, p
    quad, qp = best_q, best_p

# ----------------- OUTPUT -----------------
st.markdown(f"""
<div class="card">
  <div class="heading">เด่น / รอง (เน้นหลักสิบ-หน่วย) — ใช้เฉพาะ 10 งวดล่าสุด</div>
  <div class="num-xl">
    <span><span class="label">เด่น</span><span class="digit digit-red">{main}</span>
    <span class="tag">conf ~ {conf[main]*100:.0f}%</span></span>
    <span><span class="label">รอง</span><span class="digit digit-red">{sub}</span>
    <span class="tag">conf ~ {conf[sub]*100:.0f}%</span></span>
  </div>
</div>
""", unsafe_allow_html=True)

# 2 ตัว
pairs_html = "  ".join([
    f"<span class='badge'><span class='digit-red'>{p}</span><span class='perc'>{pct(prob)}</span></span>"
    for p, prob in pairs
]) if pairs else "<span class='perc'>ไม่พอข้อมูลคัด 2 ตัว</span>"
st.markdown(f"<div class='card'><div class='heading'>สองตัวคู่ (บน-ล่าง ไม่สลับ) — 5 ชุด</div><div class='num-lg'>{pairs_html}</div></div>", unsafe_allow_html=True)

# 3 ตัว
triples_html = "  ".join([
    f"<span class='badge'><span class='digit-red'>{t}</span><span class='perc'>{pct(prob)}</span></span>"
    for t, prob in triples
]) if triples else "<span class='perc'>ยังคัดไม่ได้ (ข้อมูลไม่พอ)</span>"
st.markdown(f"<div class='card'><div class='heading'>สามตัวล่าง — 5 ชุด</div><div class='num-md'>{triples_html}</div></div>", unsafe_allow_html=True)

# 4 ตัว
quad_html = (f"<span class='badge'><span class='digit-red'>{quad}</span><span class='perc'>{pct(qp)}</span></span>"
             if quad != "-" else "<span class='perc'>ยังคัดไม่ได้</span>")
st.markdown(f"<div class='card'><div class='heading'>สี่ตัว (จากสามตัวอันดับ 1 + หลักพัน)</div><div class='num-sm'>{quad_html}</div></div>", unsafe_allow_html=True)

st.markdown('<div class="footer">ลิขสิทธิ์@Phatarit#2025</div>', unsafe_allow_html=True)
