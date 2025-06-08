
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import os
import plotly.graph_objects as go

st.set_page_config(page_title="LottoAI", page_icon="🎯")
st.title("🎯 LottoAI – วิเคราะห์เลขเด็ดด้วย AI")

today_code = datetime.today().strftime("VIP%y%m%d")

st.subheader("📋 กรอกข้อมูลหวยย้อนหลัง (สามตัวบน และสองตัวล่าง ใช้ช่องว่างคั่น เช่น 538 29)")
data_input = st.text_area("วางข้อมูลย้อนหลังครั้งเดียวได้เลย", height=200)

extra_inputs = []
with st.expander("➕ เพิ่มข้อมูลทีละงวด"):
    for i in range(1, 6):
        val = st.text_input(f"งวดที่เพิ่ม #{i} (สามตัวบน เว้นวรรค สองตัวล่าง)", key=f"extra_{i}")
        if val:
            extra_inputs.append(val)

all_input = data_input.strip().split("\n") + extra_inputs
draws = []
for line in all_input:
    try:
        top, bottom = line.strip().split()
        draws.append((top, bottom))
    except:
        continue

if len(draws) < 5:
    st.warning("⚠️ ต้องมีข้อมูลอย่างน้อย 5 งวด")
    st.stop()

df = pd.DataFrame(draws, columns=["สามตัวบน", "สองตัวล่าง"])
st.success(f"📌 พบข้อมูล {len(df)} งวด")
st.dataframe(df)

# วิเคราะห์แบบธรรมดา (5 งวด)
if st.button("🔍 ทำนายแบบธรรมดา (5 งวดล่าสุด)"):
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
    fig.update_layout(title_text="📊 ความถี่เลข 0–9 (5 งวด)")
    st.plotly_chart(fig, use_container_width=True)

    top3 = [num for num, _ in freq.most_common(3)]
    missing = sorted(set("0123456789") - set(freq.keys()))
    st.write("🔺 เลขเด่น:", ", ".join(top3))
    st.write("🔻 เลขดับ:", ", ".join(missing))

    if len(top3) >= 2:
        two_digits = [a + b for a in top3 for b in top3 if a != b][:4]
        st.markdown("### 🎯 ชุดเลขสองตัว (แนะนำ)")
        st.markdown(f"**{' '.join(two_digits)}**")

    st.markdown("### 🔮 แนวโน้มเลขถัดไป")
    st.markdown(f"<h1 style='color:red; text-align:center'>{top3[0]}</h1>", unsafe_allow_html=True)

# ระบบ Premium
if "unlocked_until" not in st.session_state:
    st.session_state.unlocked_until = datetime.now() - timedelta(minutes=1)

st.markdown("---")
st.subheader("💎 ทำนายขั้นสูง (Premium)")

with st.expander("🔓 แนบสลิปเพื่อปลดล็อก"):
    st.image("https://promptpay.io/0869135982/59", caption="PromptPay 59 บาท", width=250)
    uploaded = st.file_uploader("📎 แนบสลิป (.jpg, .png)", type=["jpg", "png"])
    if uploaded:
        os.makedirs("slips", exist_ok=True)
        filename = f"slips/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, "wb") as f:
            f.write(uploaded.read())
        st.success(f"🎉 ขอบคุณสำหรับการสนับสนุน! รหัสของคุณคือ: {today_code}")
        st.session_state.unlocked_until = datetime.now() + timedelta(hours=24)

if datetime.now() < st.session_state.unlocked_until:
    st.markdown("### 🔮 ผลพรีเมียม (วิเคราะห์จากทุกงวด)")
    all_digits = "".join("".join(row) for row in df.values)
    freq_all = Counter(all_digits)
    top3 = [num for num, _ in freq_all.most_common(3)]
    all_two = [a + b for a in top3 for b in top3 if a != b][:4]
    st.markdown(f"<h2 style='color:red'>สองตัวบน: {' '.join(all_two)}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สองตัวล่าง: {' '.join(all_two[::-1])}</h2>", unsafe_allow_html=True)
    top3str = "".join(top3[:3])
    st.markdown(f"<h2 style='color:red'>สามตัวบน: {top3str}</h2>", unsafe_allow_html=True)

    st.markdown("### 🧩 เลขลากจาก " + top3str)
    dragged = [f"{i}{top3str[1:]}" for i in range(10)]
    st.write(", ".join(dragged))
else:
    st.warning("🔒 แนบสลิปเพื่อดูผลพรีเมียม")
