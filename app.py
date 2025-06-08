
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
import os

st.set_page_config(page_title="LottoAI Premium", page_icon="🎯")
st.title("🎯 LottoAI – วิเคราะห์เลขเด็ดด้วย AI")

today_code = datetime.today().strftime("VIP%y%m%d")

lang = st.sidebar.radio("🌐 Language / ภาษา", ("ไทย", "English"))

st.header("📋 กรอกสถิติหวยย้อนหลัง 10 งวด")
st.write("เช่น: 123 45")

data_input = st.text_area("วางข้อมูล", height=200)
if data_input:
    try:
        lines = [line.strip() for line in data_input.strip().split("\n") if line.strip()]
        draws = []
        for line in lines:
            top3, bottom2 = line.split()
            draws.append((top3, bottom2))
        df = pd.DataFrame(draws, columns=["สามตัวบน", "สองตัวล่าง"])
        st.success("✅ ข้อมูลถูกต้อง")
        st.dataframe(df)
    except:
        st.error("❌ รูปแบบข้อมูลไม่ถูกต้อง ต้องใช้ช่องว่าง เช่น 123 45")
else:
    df = None

if df is not None and len(df) >= 5:
    if st.button("🔍 ทำนายแบบธรรมดา"):
        last5 = df.tail(5)
        digits = "".join("".join(row) for row in last5.values)
        freq = Counter(digits)
        pie_data = pd.DataFrame(freq.items(), columns=["เลข", "ความถี่"])
        st.subheader("📊 ความถี่เลข 0–9 (5 งวดย้อนหลัง)")
        st.bar_chart(pie_data.set_index("เลข"))

        top3 = [num for num, _ in freq.most_common(3)]
        missing = sorted(set("0123456789") - set(freq.keys()))
        st.write("🔺 เลขเด่น:", ", ".join(top3))
        st.write("🔻 เลขดับ:", ", ".join(missing))
        st.markdown("### 🔮 แนวโน้มเลขถัดไป")
        st.markdown(f"<h1 style='color:red; text-align:center'>{top3[0]}</h1>", unsafe_allow_html=True)

# พรีเมียม
st.markdown("---")
st.subheader("💎 ทำนายขั้นสูง (Premium)")

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

with st.expander("🔓 แนบสลิปเพื่อรับรหัสพรีเมียม"):
    st.image("https://promptpay.io/0869135982/59", caption="PromptPay 59 บาท", width=250)
    uploaded = st.file_uploader("📎 แนบสลิป (.jpg, .png)", type=["jpg", "png"])
    if uploaded:
        os.makedirs("slips", exist_ok=True)
        filename = f"slips/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, "wb") as f:
            f.write(uploaded.read())
        st.success(f"🎉 ขอบคุณสำหรับการสนับสนุน!\nรหัสของคุณคือ: {today_code}")
        st.session_state.unlocked = True

if st.session_state.unlocked:
    st.markdown("### 🔮 เลขพรีเมียม")
    st.markdown(f"<h2 style='color:red'>สองตัวบน: 83, 91, 75, 40</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สองตัวล่าง: 29, 10, 58, 63</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สามตัวบน: 583</h2>", unsafe_allow_html=True)
else:
    st.warning("🔒 แนบสลิปเพื่อดูผลพรีเมียม")
