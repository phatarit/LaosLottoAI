import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from itertools import permutations
import os
import plotly.graph_objects as go

st.set_page_config(page_title="LottoAI", page_icon="🎯")
st.title("🎯 LottoAI – Lotto Analyzer (Premium v2)")

today_code = datetime.today().strftime("VIP%y%m%d")

# ---------- Input zone ----------
st.subheader("📋 กรอกข้อมูลหวยย้อนหลัง (สามตัวบน และสองตัวล่าง ใช้ช่องว่างคั่น เช่น 538 29)")
data_input = st.text_area("วางข้อมูลย้อนหลังครั้งเดียวได้เลย", height=200)

extra_inputs = []
with st.expander("➕ เพิ่มข้อมูลทีละงวด"):
    for i in range(1, 6):
        val = st.text_input(f"งวดที่เพิ่ม #{i} (สามตัวบน เว้นวรรค สองตัวล่าง)", key=f"extra_{i}")
        if val:
            extra_inputs.append(val)

all_input = data_input.strip().split("\n") + extra_inputs
draws = []
for line in all_input:
    if not line.strip():
        continue
    try:
        top, bottom = line.strip().split()
        if len(top) == 3 and len(bottom) == 2 and top.isdigit() and bottom.isdigit():
            draws.append((top, bottom))
    except ValueError:
        continue

if len(draws) < 5:
    st.warning("⚠️ ต้องมีข้อมูลอย่างน้อย 5 งวด")
    st.stop()

df = pd.DataFrame(draws, columns=["สามตัวบน", "สองตัวล่าง"])
st.success(f"📌 พบข้อมูล {len(df)} งวด")
st.dataframe(df)

# ---------- Helper : สูตรขั้นสูง ----------
def predict_premium(df: pd.DataFrame):
    """Return advanced predictions using 6 empirical formulas."""
    draws = list(df[['สามตัวบน', 'สองตัวล่าง']].itertuples(index=False, name=None))
    all_digits = "".join("".join(pair) for pair in draws)

    # 1) HOT digits (frequency)
    hot_digits = [d for d, _ in Counter(all_digits).most_common(5)]

    # 2) RUN digits (come from last bottom)
    last_top, last_bottom = draws[-1]
    run_digits = list(last_bottom)

    # 3) Sum‑mod (สูตร 4)
    sum_mod = str(sum(int(d) for d in last_top) % 10)

    # 4) Pair‑reverse (สูตร 5)
    pair_reverse = last_bottom[::-1]

    # Collect unique candidate digits in meaningful order
    candidate_digits = []
    for d in run_digits + [sum_mod] + hot_digits:
        if d not in candidate_digits:
            candidate_digits.append(d)
    # Guarantee at least 6 unique digits
    while len(candidate_digits) < 6:
        candidate_digits.append(str((int(candidate_digits[-1]) + 1) % 10))

    # 5) High‑Low / Odd‑Even switching (สูตร 6) for 2‑digit filter
    def high_low_switch(num: str) -> bool:
        last_even = int(last_bottom[-1]) % 2 == 0
        want_odd  = last_even  # ถ้าล่างล่าสุด “คู่” ให้สลับเป็น “คี่”
        return (int(num[1]) % 2 == 1) if want_odd else True

    two_predictions = []
    for a in candidate_digits:
        for b in candidate_digits:
            if a == b:
                continue  # งดเบิ้ล (สูตร 2 คาดว่าเบิ้ลพัก)
            num = a + b
            if high_low_switch(num):
                two_predictions.append(num)
    two_predictions = two_predictions[:12]

    # 6) Build three‑digit candidates (avoid double & permutations of first 6 candidates)
    three_predictions = []
    for perm in permutations(candidate_digits, 3):
        if perm[0] != perm[1] != perm[2]:
            three_predictions.append("".join(perm))
        if len(three_predictions) == 10:
            break

    return two_predictions, three_predictions, candidate_digits, sum_mod, pair_reverse

# ---------- Normal analysis (5 งวด) ----------
if st.button("🔍 ทำนายแบบธรรมดา (5 งวดล่าสุด)"):
    recent = df.tail(5)
    digits = "".join("".join(row) for row in recent.values)
    freq = Counter(digits)
    pie_data = pd.DataFrame(freq.items(), columns=["เลข", "ความถี่"])
    pie_data["ร้อยละ"] = pie_data["ความถี่"] / pie_data["ความถี่"].sum() * 100

    colors = ["#FF9999", "#FFCC99", "#FFFF99", "#CCFF99", "#99FF99",
              "#99FFFF", "#99CCFF", "#9999FF", "#CC99FF", "#FF99CC"]

    fig = go.Figure(data=[go.Pie(labels=pie_data["เลข"],
                                 values=pie_data["ร้อยละ"],
                                 textinfo='label+percent',
                                 marker=dict(colors=colors),
                                 hole=0.3)])
    fig.update_layout(title_text="📊 ความถี่เลข 0–9 (5 งวด)")
    st.plotly_chart(fig, use_container_width=True)

    top3 = [num for num, _ in freq.most_common(3)]
    missing = sorted(set("0123456789") - set(freq.keys()))
    st.write("🔺 เลขเด่น:", ", ".join(top3))
    st.write("🔻 เลขดับ:", ", ".join(missing))

    if len(top3) >= 2:
        two_digits = [a + b for a in top3 for b in top3 if a != b][:4]
        st.markdown("### 🎯 ชุดเลขสองตัว (แนะนำ)")
        st.markdown(f"**{' '.join(two_digits)}**")

    st.markdown("### 🔮 แนวโน้มเลขถัดไป")
    st.markdown(f"<h1 style='color:red; text-align:center'>{top3[0]}</h1>", unsafe_allow_html=True)

# ---------- Premium zone ----------
if "unlocked_until" not in st.session_state:
    st.session_state.unlocked_until = datetime.now() - timedelta(minutes=1)

st.markdown("---")
st.subheader("💎 ทำนายขั้นสูง (Premium)")

with st.expander("🔓 แนบสลิปเพื่อปลดล็อก"):
    st.image("https://promptpay.io/0869135982/59", caption="PromptPay 59 บาท", width=250)
    uploaded = st.file_uploader("📎 แนบสลิป (.jpg, .png)", type=["jpg", "png"])
    if uploaded:
        os.makedirs("slips", exist_ok=True)
        filename = f"slips/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, "wb") as f:
            f.write(uploaded.read())
        st.success(f"🎉 ขอบคุณสำหรับการสนับสนุน! รหัสของคุณคือ: {today_code}")
        st.session_state.unlocked_until = datetime.now() + timedelta(hours=24)

if datetime.now() < st.session_state.unlocked_until:
    st.markdown("### 🔮 ผลพรีเมียม (สูตรขั้นสูง)")
    two_preds, three_preds, cand_digits, sum_mod, pair_rev = predict_premium(df)

    st.markdown(f"**สองตัว (บน/ล่าง):** {' '.join(two_preds)}")
    st.markdown(f"**สามตัวบน:** {' '.join(three_preds)}")
    st.markdown(f"**แต้มผลรวม (sum mod 10):** {sum_mod}")
    st.markdown(f"**คู่กลับล่าสุด:** {pair_rev}")
    st.markdown(f"**ชุดตัววิ่ง (candidate digits):** {', '.join(cand_digits)}")

    # เสริม “เลขลาก” เช่นเดิม
    st.markdown("### 🧩 เลขลากจาก " + three_preds[0])
    dragged = [f"{i}{three_preds[0][1:]}" for i in range(10)]
    st.write(", ".join(dragged))
else:
    st.warning("🔒 แนบสลิปเพื่อดูผลพรีเมียม")

st.caption("© 2025 LottoAI – Advanced Edition")
