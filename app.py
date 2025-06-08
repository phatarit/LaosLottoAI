
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import os

st.set_page_config(page_title="LottoAI Premium", page_icon="🎯")
st.title("🎯 LottoAI – วิเคราะห์เลขเด็ดด้วย AI")

today_code = datetime.today().strftime("VIP%y%m%d")

# ภาษา
lang = st.sidebar.radio("🌐 Language / ภาษา", ("ไทย", "English"))
L = {
    "title": "LottoAI – วิเคราะห์เลขเด็ดด้วย AI" if lang == "ไทย" else "LottoAI – Lucky Number Predictor",
    "input": "วางข้อมูลหวยย้อนหลัง (ใช้เว้นวรรค เช่น 123 45)" if lang == "ไทย" else "Paste past lottery results (format: 123 45)",
    "analyze": "🔍 ทำนายแบบธรรมดา" if lang == "ไทย" else "🔍 Basic Prediction",
    "premium": "💎 ทำนายขั้นสูง (Premium)" if lang == "ไทย" else "💎 Premium Prediction",
    "upload": "📎 แนบสลิป (.jpg, .png)" if lang == "ไทย" else "📎 Upload payment slip (.jpg, .png)",
    "unlocked": "🎉 ขอบคุณสำหรับการสนับสนุน!\nรหัสของคุณคือ: " if lang == "ไทย" else "🎉 Thank you for your support!\nYour code is: ",
    "renew": "🔁 ต่ออายุ Premium (แนบสลิปใหม่)" if lang == "ไทย" else "🔁 Renew Premium Access",
    "locked": "🔒 แนบสลิปเพื่อดูผลพรีเมียม" if lang == "ไทย" else "🔒 Upload slip to unlock premium",
}

# กรอกข้อมูลย้อนหลัง
st.header("📋 " + L["input"])
data_input = st.text_area("", height=200)
df = None
if data_input:
    try:
        lines = [line.strip() for line in data_input.strip().split("\n") if line.strip()]
        draws = [line.split() for line in lines]
        df = pd.DataFrame(draws, columns=["สามตัวบน", "สองตัวล่าง"])
        st.success("✅ ข้อมูลถูกต้อง")
        st.dataframe(df)
    except:
        st.error("❌ รูปแบบข้อมูลผิด ต้องใช้เว้นวรรค เช่น 123 45")

# ทำนายธรรมดา
if df is not None and len(df) >= 5:
    if st.button(L["analyze"]):
        last5 = df.tail(5)
        digits = "".join("".join(row) for row in last5.values)
        freq = Counter(digits)
        pie_data = pd.DataFrame(freq.items(), columns=["เลข", "ความถี่"])
        pie_data["ร้อยละ"] = pie_data["ความถี่"] / pie_data["ความถี่"].sum() * 100
        st.subheader("📊 ความถี่เลข 0–9 (5 งวด)")
        st.plotly_chart(pie_data.set_index("เลข").plot.pie(y="ร้อยละ", autopct="%.1f%%", ylabel="", legend=False, figsize=(4,4)), use_container_width=True)

        top3 = [num for num, _ in freq.most_common(3)]
        missing = sorted(set("0123456789") - set(freq.keys()))
        st.write("🔺 เลขเด่น:", ", ".join(top3))
        st.write("🔻 เลขดับ:", ", ".join(missing))

        # แสดงเลขสองตัว 4 ชุด
        st.markdown("### 🎯 ชุดเลขสองตัว (แนะนำ)")
        if len(top3) >= 2:
            two_digits = [a + b for a in top3 for b in top3 if a != b][:4]
            st.markdown(f"**{' '.join(two_digits)}**")

        st.markdown("### 🔮 แนวโน้มเลขถัดไป")
        st.markdown(f"<h1 style='color:red; text-align:center'>{top3[0]}</h1>", unsafe_allow_html=True)

# ระบบปลดล็อก Premium
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

# ต่ออายุ
if is_unlocked:
    if st.button(L["renew"]):
        st.session_state.unlocked_until = datetime.now() - timedelta(minutes=1)
        st.experimental_rerun()

# พรีเมียมโชว์
if datetime.now() < st.session_state.unlocked_until:
    st.markdown("### 🔮 เลขพรีเมียม")
    st.markdown(f"<h2 style='color:red'>สองตัวบน: 83, 91, 75, 40</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สองตัวล่าง: 29, 10, 58, 63</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สามตัวบน: 538</h2>", unsafe_allow_html=True)

    # เลขลาก
    st.markdown("### 🧩 เลขลากจาก 538")
    base = "538"[1:]
    dragged = [f"{i}{base}" for i in range(10)]
    st.write(", ".join(dragged))
else:
    st.warning(L["locked"])
