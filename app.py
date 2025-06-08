import streamlit as st, pandas as pd
from collections import Counter, defaultdict
from itertools import permutations, combinations, islice

# ───── CONFIG ─────
MIN_HISTORY = 10                 # <<-- จาก 40 → 10
WIN_EXPHOT  = 10                 # ใช้ 10 งวดล่าสุดคำนวณ EXP-HOT
WIN_TRANS   = 10                 # Markov เริ่มเดินหลังมี 10 งวด

st.set_page_config(page_title='ThaiLottoAI v3.4', page_icon='🎯')
st.title('🎯 ThaiLottoAI – Mini-Dataset (10 draws)')

# ───── INPUT ─────
raw = st.text_area('3 ตัวบน เว้นวรรค 2 ตัวล่าง (1 บรรทัด/งวด)', height=250)
draws=[]
for ln in raw.splitlines():
    try:
        t,b=ln.split(); 
        if len(t)==3 and len(b)==2:
            draws.append((t,b))
    except: pass

if len(draws) < MIN_HISTORY:
    st.info(f'⚠️ ต้องมีข้อมูล ≥ {MIN_HISTORY} งวด')
    st.stop()

st.dataframe(pd.DataFrame(draws,columns=['สามตัวบน','สองตัวล่าง']),
             use_container_width=True)

# ───── HELPERS ─────
def hot(hist,n=3):
    return [d for d,_ in Counter(''.join(''.join(p) for p in hist)).most_common(n)]

def unordered2(x): return ''.join(sorted(x))
def unordered3(x): return ''.join(sorted(x))
def pretty(lst,n=10): return '<br>'.join('  '.join(lst[i:i+n]) 
                                        for i in range(0,len(lst),n))

# ───── EXP-HOT (ตัวเด่น) ─────
def exp_hot(hist):
    sc=Counter()
    for i,(t,b) in enumerate(reversed(hist[-WIN_EXPHOT:])):
        w=0.8**i
        for d in t+b: sc[d]+=w
    for d in hot(hist[-WIN_EXPHOT:]): sc[d]+=0.3
    return max(sc,key=sc.get)

# ───── Markov-20 (10 draws) ─────
def trans(hist):
    M=defaultdict(Counter)
    for (pt,pb),(ct,cb) in zip(hist[:-1],hist[1:]):
        M[unordered2(pb)][unordered2(cb)]+=1
    return M

def pairs20(hist):
    last=unordered2(hist[-1][1])
    base=[p for p,_ in trans(hist)[last].most_common(20)]
    for a,b in combinations(hot(hist),2):
        p=unordered2(a+b)
        if p not in base: base.append(p)
        if len(base)==20: break
    return base[:20]

# ───── Hybrid-20 (10 draws) ─────
def combos20(hist):
    pool=list(dict.fromkeys(
        list(hist[-1][1])+hot(hist,3)))[:12]
    triples={' '.join(sorted(c)) for c in combinations(pool,3)}
    return list(islice(triples,20))

# ───── Hit functions ─────
two_hit = lambda P,act: unordered2(act[1]) in P or unordered2(act[0][1:]) in P
three_hit=lambda P,act: unordered3(act[0]) in P

def walk(hist,pred,hit,start):
    hit_cnt=tot=0
    for i in range(start,len(hist)):
        if hit(pred(hist[:i]),hist[i]): hit_cnt+=1
        tot+=1
    return hit_cnt/tot if tot else 0

acc_two   = walk(draws,pairs20,two_hit,WIN_TRANS)
acc_three = walk(draws,combos20,three_hit,WIN_TRANS)

# ───── Predict next ─────
single   = exp_hot(draws)
two20    = pairs20(draws)
three20  = combos20(draws)
focus_two = two20[:5]; focus_three=three20[0]

# ───── DISPLAY ─────
st.markdown(f"<div style='font-size:40px;color:red;text-align:center'>ตัวเด่น: {single}</div>",
            unsafe_allow_html=True)

c1,c2=st.columns(2)
with c1:
    st.subheader('สองตัว (20 ชุด)')
    st.markdown(f"<div style='font-size:22px;color:red'>{pretty(two20,10)}</div>",
                unsafe_allow_html=True)
    st.caption(f"Hit≈{acc_two*100:.1f}%")

with c2:
    st.subheader('สามตัว (20 ชุด)')
    st.markdown(f"<div style='font-size:22px;color:red'>{pretty(three20,10)}</div>",
                unsafe_allow_html=True)
    st.caption(f"Hit≈{acc_three*100:.1f}%")

st.subheader('🚩 เลขเจาะ')
st.markdown(f"<div style='font-size:26px;color:red'>สองตัว: {'  '.join(focus_two)}<br>"
            f"สามตัว: {focus_three}</div>", unsafe_allow_html=True)

st.caption('© 2025 ThaiLottoAI v3.4 – Min-10 draws')
