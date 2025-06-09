import streamlit as st
import pandas as pd
from collections import Counter, defaultdict
from itertools import combinations

# ─────────────────── CONFIG ───────────────────
st.set_page_config(page_title="YKLottaAI", page_icon="🎯", layout="centered")
st.title("🎯 YKLottaAI")

# ────────────────── SESSION STATE ──────────────────
if "history_raw" not in st.session_state:
    st.session_state.history_raw = ""

# ────────────────── INPUT ──────────────────
st.markdown("วางผลย้อนหลัง **สามตัวบน เว้นวรรค สองตัวล่าง** ต่อเนื่องกันคนละบรรทัด เช่น `774 81`")
raw = st.text_area("📋 ข้อมูลย้อนหลัง", value=st.session_state.history_raw, height=250)

col_save, col_clear = st.columns(2)
with col_save:
    if st.button("💾 บันทึกข้อมูล"):
        st.session_state.history_raw = raw
        st.success("บันทึกข้อมูลเรียบร้อย ✔")
with col_clear:
    if st.button("🗑 ล้างข้อมูลที่บันทึก"):
        st.session_state.history_raw = ""
        st.success("ล้างข้อมูลแล้ว")

# ────────────────── PARSE DRAWS ──────────────────

draws = []
for idx, line in enumerate(raw.splitlines(), 1):
    try:
        t, b = line.split()
        if len(t) == 3 and len(b) == 2 and t.isdigit() and b.isdigit():
            draws.append((t, b))
        else:
            st.warning(f"ข้ามบรรทัด {idx}: รูปแบบผิด → {line}")
    except ValueError:
        if line.strip():
            st.warning(f"ข้ามบรรทัด {idx}: ไม่พบช่องว่าง → {line}")

if len(draws) < 15:
    st.info("⚠️ ต้องมีข้อมูล ≥ 15 งวด")
    st.stop()

st.dataframe(pd.DataFrame(draws, columns=["สามตัวบน", "สองตัวล่าง"]), use_container_width=True)

# ────────────────── HELPER FUNCTIONS ──────────────────

def hot_digits(hist, win, n=3):
    seg = hist[-win:] if len(hist) >= win else hist
    return [d for d, _ in Counter("".join("".join(x) for x in seg)).most_common(n)]

def pretty(lst, per_line=10):
    chunk = ["  ".join(lst[i : i + per_line]) for i in range(0, len(lst), per_line)]
    return "<br>".join(chunk)

def unordered2(p):
    return "".join(sorted(p))

def unordered3(t):
    return "".join(sorted(t))

def run_digits(hist):
    return list(hist[-1][1])

def sum_mod(hist):
    return str(sum(map(int, hist[-1][0])) % 10)

# windows 10,15,20,25,30
hot10  = hot_digits(draws, 10)
hot15  = hot_digits(draws, 15)
hot20  = hot_digits(draws, 20)
hot25  = hot_digits(draws, 25)
hot30  = hot_digits(draws, 30)

# ────────────────── CORE ALGORITHMS ──────────────────

def exp_hot(hist, win=27):
    sc = Counter()
    for i, (t, b) in enumerate(reversed(hist[-win:])):
        w = 0.8 ** i
        for d in t + b:
            sc[d] += w
    for d in hot10 + hot15 + hot20 + hot25 + hot30:
        sc[d] += 0.3
    return max(sc, key=sc.get)


def build_trans(hist):
    M = defaultdict(Counter)
    for (pt, pb), (ct, cb) in zip(hist[:-1], hist[1:]):
        M[unordered2(pb)][unordered2(cb)] += 1
    return M


def markov_pairs(hist, size=10):
    trans = build_trans(hist)
    last = unordered2(hist[-1][1])
    base = [p for p, _ in trans[last].most_common(size)]

    boost = set(hot10 + hot15 + hot20 + hot25 + hot30)
    for a, b in combinations(boost, 2):
        p = unordered2(a + b)
        if p not in base:
            base.append(p)
        if len(base) == size:
            break
    return base[:size]


def hybrid_combos(hist, pool_sz=12, k=10):
    pool = (
        run_digits(hist)
        + [sum_mod(hist)]
        + hot_digits(hist, 5, 3)
        + hot_digits(hist, len(hist), 3)
        + hot10
        + hot15
        + hot20
        + hot25
        + hot30
    )
    pool = list(dict.fromkeys(pool))[:pool_sz]

    score = Counter()
    for i, (t, b) in enumerate(hist[-30:]):
        w = 1 - i / 30 * 0.9
        for d in t + b:
            score[d] += w

    combos = {"".join(sorted(c)) for c in combinations(pool, 3)}
    combos = sorted(combos, key=lambda x: -(score[x[0]] + score[x[1]] + score[x[2]]))
    return combos[:k]

# ────────────────── PREDICT NEXT ──────────────────

main_digit = exp_hot(draws)
combo_two  = markov_pairs(draws, size=10)  # 10 ชุด
combo_three = hybrid_combos(draws, k=10)   # 10 ชุด

# รวม 2 ตัวท้ายบนเข้าชุดล่าง
for tail in {unordered2(t[1:]) for t, _ in [draws[-1]]}:
    if tail not in combo_two and len(combo_two) < 10:
        combo_two.append(tail)

focus_two   = combo_two[:5]
focus_three = combo_three[:3]

# ────────────────── DISPLAY RESULTS ──────────────────

st.markdown(
    f"<div style='font-size:44px;color:red;text-align:center'>รูด 19 ประตู: {main_digit}</div>",
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)
with c1:
    st.subheader("เจาะสองตัว (10 ชุด)")
    st.markdown(
        f"<div style='font-size:22px;color:red'>{pretty(combo_two,10)}</div>",
        unsafe_allow_html=True,
    )

with c2:
    st.subheader("เจาะสามตัวกลับ 6 ทาง (10 ชุด)")
    st.markdown(
        f"<div style='font-size:22px;color:red'>{pretty(combo_three,10)}</div>",
        unsafe_allow_html=True,
    )

st.subheader("🚩 เลขเจาะ")
st.markdown(
    f"<div style='font-size:26px;color:red'>สองตัว (5 ชุด): {'  '.join(focus_two)}<br>"
    f"สามตัว (3 ชุด): {'  '.join(focus_three)}</div>",
    unsafe_allow_html=True,
)

# ────────────────── FOOTER ──────────────────
st.caption("© 2025 YKLottaAI")
