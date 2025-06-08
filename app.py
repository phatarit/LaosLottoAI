
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
import os

st.set_page_config(page_title="LottoAI Premium", page_icon="🎯")
st.title("🎯 LottoAI – วิเคราะห์เลขเด็ดด้วย AI")

# ===== Dynamic premium code based on date =====
today_code = datetime.today().strftime("VIP%y%m%d")

# ===== Sidebar language =====
lang = st.sidebar.radio("🌐 ภาษา / Language", ("ไทย", "English"))

# ===== Input lottery history =====
st.header("📋 กรอกสถิติหวยย้อนหลัง 10 งวด")
st.write("รูปแบบ: สามตัวบน, สองตัวล่าง (เช่น: 123, 45)")

data_input = st.text_area("วางข้อมูลที่นี่", height=200)
if data_input:
    try:
        lines = [line.strip() for line in data_input.strip().split("\n") if line.strip()]
        draws = []
        for line in lines:
            top3, bottom2 = map(str.strip, line.split(","))
            draws.append((top3, bottom2))
        df = pd.DataFrame(draws, columns=["สามตัวบน", "สองตัวล่าง"])
        st.success("✅ นำเข้าข้อมูลสำเร็จแล้ว")
        st.dataframe(df)
    except:
        st.error("❌ รูปแบบข้อมูลไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง")
else:
    df = None

# ===== Basic Analysis =====
if df is not None and len(df) >= 5:
    if st.button("🔍 ทำนายแบบธรรมดา"):
        last5 = df.tail(5)
        digits = "".join("".join(row) for row in last5.values)
        freq = Counter(digits)
        most_common = freq.most_common()
        pie_data = pd.DataFrame(most_common, columns=["เลข", "ความถี่"])
        st.subheader("📊 ความถี่เลข 0–9 (5 งวดย้อนหลัง)")
        st.bar_chart(pie_data.set_index("เลข"))

        top3 = [num for num, count in most_common[:3]]
        all_digits = set("0123456789")
        used_digits = set(d for d, c in most_common)
        missing = sorted(all_digits - used_digits)
        st.write("🔺 เลขเด่น:", ", ".join(top3))
        st.write("🔻 เลขดับ:", ", ".join(missing))
        st.markdown("### 🔮 แนวโน้มเลขถัดไป")
        st.markdown(f"<h1 style='color:red; text-align:center'>{top3[0]}</h1>", unsafe_allow_html=True)

# ===== Premium Section =====
st.markdown("---")
st.subheader("💎 ทำนายขั้นสูง (Premium)")

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

with st.expander("🔐 ปลดล็อก Premium"):
    st.image("https://promptpay.io/0869135982/59", caption="PromptPay 59 บาท", width=250)
    uploaded = st.file_uploader("แนบสลิป (.jpg, .png)", type=["jpg", "png"])
    name = st.text_input("ชื่อผู้ใช้ / เบอร์โทร")
    code = st.text_input("รหัสปลดล็อก", type="password")

    if uploaded and name:
        os.makedirs("slips", exist_ok=True)
        slip_path = f"slips/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.jpg"
        with open(slip_path, "wb") as f:
            f.write(uploaded.read())
        st.success("✅ อัปโหลดสลิปสำเร็จ กรุณารอการตรวจสอบ")

    if code == today_code:
        st.session_state.unlocked = True
        st.success("✅ ปลดล็อกสำเร็จ! ใช้งาน Premium ได้แล้ว")
    elif code:
        st.error("❌ รหัสไม่ถูกต้อง หรือหมดอายุ (ใช้ได้วันต่อวัน)")

if st.session_state.unlocked:
    st.markdown("### 🔮 เลขพรีเมียม (วิเคราะห์ลึก)")
    st.markdown(f"<h2 style='color:red'>สองตัวบน: 83, 91, 75, 40</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สองตัวล่าง: 29, 10, 58, 63</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red'>สามตัวบน: 583</h2>", unsafe_allow_html=True)
else:
    st.warning("🔒 ต้องปลดล็อกเพื่อดูผลทำนายแบบพรีเมียม")

# ===== Admin Panel =====
st.markdown("---")
with st.expander("🛠 Admin Panel (เฉพาะผู้ดูแลระบบ)"):
    admin_pw = st.text_input("รหัสผ่านแอดมิน", type="password")
    if admin_pw == "admin123":
        st.success("เข้าสู่ระบบแอดมินแล้ว")
        if os.path.exists("slips"):
            files = os.listdir("slips")
            if files:
                st.write("📂 รายการสลิปที่อัปโหลด:")
                for f in sorted(files, reverse=True):
                    st.image(f"slips/{f}", caption=f, width=300)
            else:
                st.info("ยังไม่มีสลิปอัปโหลด")
        else:
            st.info("ยังไม่มีโฟลเดอร์สลิป")
    elif admin_pw:
        st.error("❌ รหัสผ่านไม่ถูกต้อง")
