
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import os
import plotly.graph_objects as go

st.set_page_config(page_title="LottoAI", page_icon="🎯")
st.title("🎯 LottoAI – วิเคราะห์เลขเด็ดด้วย AI")

lang = st.sidebar.radio("🌐 Language / ภาษา", ("ไทย", "English"))
L = {
    "input_top": "กรอกเลขสามตัวบน (เช่น 538 754 019)",
    "input_bottom": "กรอกเลขสองตัวล่าง (เช่น 29 10 58)",
    "analyze": "🔍 ทำนายแบบธรรมดา",
    "clear": "🧼 ล้างข้อมูล",
    "premium": "💎 ทำนายขั้นสูง (Premium)",
    "upload": "📎 แนบสลิป (.jpg, .png)",
    "unlocked": "🎉 ขอบคุณสำหรับการสนับสนุน!\nรหัสของคุณคือ: ",
    "renew": "🔁 ต่ออายุ Premium",
    "locked": "🔒 แนบสลิปเพื่อดูผลพรีเมียม",
}

st.subheader("📋 " + L["input_top"])
top_input = st.text_input("", key="top_input")

st.subheader(L["input_bottom"])
bottom_input = st.text_input("", key="bottom_input")

if st.button(L["clear"]):
    st.experimental_rerun()

df = None
if top_input and bottom_input:
    top = top_input.strip().split()
    bottom = bottom_input.strip().split()
    if len(top) == len(bottom):
        df = pd.DataFrame({'สามตัวบน': top, 'สองตัวล่าง': bottom})
        st.success("✅ ข้อมูลถูกต้อง")
        st.dataframe(df)
    else:
        st.error("❌ จำนวนงวดไม่ตรงกัน")

if df is not None and len(df) >= 5:
    if st.button(L["analyze"]):
        last5 = df.tail(5)
        digits = "".join("".join(row) for row in last5.values)
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
        fig.update_layout(title_text="📊 ความถี่เลข 0–9 (5 งวดย้อนหลัง)")
        st.plotly_chart(fig, use_container_width=True)

        top3 = [num for num, _ in freq.most_common(3)]
        missing = sorted(set("0123456789") - set(freq.keys()))
        st.write("🔺 เลขเด่น:", ", ".join(top3))
        st.write("🔻 เลขดับ:", ", ".join(missing))

        st.markdown("### 🎯 ชุดเลขสองตัว (แนะนำ)")
        if len(top3) >= 2:
            two_digits = [a + b for a in top3 for b in top3 if a != b][:4]
            st.markdown(f"**{' '.join(two_digits)}**")

        st.markdown("### 🔮 แนวโน้มเลขถัดไป")
        st.markdown(f"<h1 style='color:red; text-align:center'>{top3[0]}</h1>", unsafe_allow_html=True)

# Premium unlock
today_code = datetime.today().strftime("VIP%y%m%d")
if "unlocked_until" not in st.session_state:
    st.session_state.unlocked_until = datetime.now() - timedelta(minutes=1)

now = datetime.now()
is_unlocked = now < st.session_state.unlocked_until

st.markdown("---")
st.subheader(L["premium"])

with st.expander("🔓 แนบสลิปเพื่อปลดล็อก"):
    st.image("https://promptpay.io/0869135982/59", caption="PromptPay 59 บาท", width=250)
    uploaded = st.file_uploader(L["upload"], type=["jpg", "png"])
    if uploaded:
        os.makedirs("slips", exist_ok=True)
        filename = f"slips/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, "wb") as f:
            f.write(uploaded.read())
        st.success(f"{L['unlocked']}{today_code}")
        st.session_state.unlocked_until = datetime.now() + timedelta(hours=24)

if is_unlocked:
    if st.button(L["renew"]):
        st.session_state.unlocked_until = datetime.now() - timedelta(minutes=1)
        st.experimental_rerun()

if datetime.now() < st.session_state.unlocked_until:
    st.markdown("### 🔮 เลขพรีเมียม")
    st.markdown(f"<h2 style='color:red'>สองตัวบน: 83, 91, 75, 40</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สองตัวล่าง: 29, 10, 58, 63</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สามตัวบน: 538</h2>", unsafe_allow_html=True)

    st.markdown("### 🧩 เลขลากจาก 538")
    base = "538"[1:]
    dragged = [f"{i}{base}" for i in range(10)]
    st.write(", ".join(dragged))
else:
    st.warning(L["locked"])
