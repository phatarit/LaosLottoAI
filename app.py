
import streamlit as st
import random

st.set_page_config(page_title="LottoAI", page_icon="🎯", layout="centered")

lang = st.sidebar.radio("🌐 Language / ภาษา", ("ไทย", "English"))

st.title("🎯 LottoAI")
st.subheader("🔢 " + ("ทำนายเลขเด็ดด้วย AI" if lang == "ไทย" else "AI Lucky Number Predictor"))

user_input = st.text_input("กรอกเลขหรือคำถาม..." if lang == "ไทย" else "Enter numbers or query...")

if st.button("🔍 ทำนาย" if lang == "ไทย" else "🔍 Predict"):
    lucky_number = random.randint(0, 999)
    result = f"เลขเด่นวันนี้คือ: {lucky_number:03d}" if lang == "ไทย" else f"Today’s lucky number is: {lucky_number:03d}"
    st.success(result)
    st.info("โชคดีในการเสี่ยงโชค!" if lang == "ไทย" else "Good luck!")

    # Copy / Download options
    st.download_button(
        label="📥 ดาวน์โหลดผล" if lang == "ไทย" else "📥 Download Result",
        data=result,
        file_name="lotto_result.txt",
        mime="text/plain"
    )

# Placeholder for ads
st.markdown("---")
st.markdown("🟨 พื้นที่สำหรับโฆษณา / Ad Banner Placeholder", unsafe_allow_html=True)

# Social share
st.markdown("#### 📤 แชร์แอป")
fb_url = f"https://www.facebook.com/sharer/sharer.php?u=https://lotto-ai.streamlit.app"
line_url = f"https://social-plugins.line.me/lineit/share?url=https://lotto-ai.streamlit.app"
st.markdown(f"[แชร์ผ่าน Facebook]({fb_url}) | [แชร์ผ่าน LINE]({line_url})")
