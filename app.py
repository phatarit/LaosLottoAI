import streamlit as st
import pandas as pd
from collections import Counter

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

def dead_digits_09(draws, n=5):
    """
    คืนค่าเลข 0-9 ที่ไม่ออกเลยในทั้งสามตัวบนและสองตัวล่าง (ทุกหลัก) ใน n งวดล่าสุด
    """
    last_draws = draws[-n:]
    appeared = set()
    for t, b in last_draws:
        appeared.update(t)
        appeared.update(b)
    all_digits = set(str(i) for i in range(10))
    dead = sorted(all_digits - appeared)
    return dead

def even_odd_chain(draws, n=3):
    """
    ตรวจแต่ละหลัก (ร้อย/สิบ/หน่วยบน, สิบ/หน่วยล่าง) ว่าเลขคู่หรือคี่ออกซ้ำ n รอบติดหรือไม่
    คืนค่า: [(หลัก, คู่/คี่, เลขกลุ่มนั้น top 3), ...]
    """
    results = []
    idx_map = [
        ('หลักร้อยบน', lambda t, b: int(t[0])),
        ('หลักสิบบน',  lambda t, b: int(t[1])),
        ('หลักหน่วยบน',lambda t, b: int(t[2])),
        ('หลักสิบล่าง', lambda t, b: int(b[0])),
        ('หลักหน่วยล่าง',lambda t, b: int(b[1])),
    ]
    for label, func in idx_map:
        seq = [func(t, b) for t, b in draws[-n:]]
        if all(x % 2 == 0 for x in seq):  # คู่ซ้ำ n รอบ
            all_vals = [func(t, b) for t, b in draws]
            odd_freq = Counter([x for x in all_vals if x % 2 == 1]).most_common(3)
            results.append((label, 'คู่', odd_freq))
        elif all(x % 2 == 1 for x in seq):  # คี่ซ้ำ n รอบ
            all_vals = [func(t, b) for t, b in draws]
            even_freq = Counter([x for x in all_vals if x % 2 == 0]).most_common(3)
            results.append((label, 'คี่', even_freq))
    return results

def top3_freq_digits(draws):
    """
    เลขเด่นสุด 3 อันดับ (ทุกหลักในสามตัวบน+สองตัวล่าง)
    """
    digits = "".join(t + b for t, b in draws)
    return [d for d, _ in Counter(digits).most_common(3)]

# ────────────────── MAIN PREDICT LOGIC ──────────────────

# สูตร 1: ถ้ามีหลักใดคู่/คี่ซ้ำ 3 งวดติด
eo_results = even_odd_chain(draws, n=3)
two_digit_sets = []
three_digit_sets = []
explain_msg = ""
if eo_results:
    explain_msg = "🔮 **สูตรอันดับ 1:** เจอเหตุการณ์เลขคู่/คี่ออกซ้ำ 3 รอบในหลักต่อไปนี้"
    # ใช้เฉพาะหลักแรกที่เจอ
    label, last_type, freq_list = eo_results[0]
    freq_digits = [str(x[0]) for x in freq_list if x[1] > 0]
    dead_digits = dead_digits_09(draws, n=5)
    # สร้างสองตัวบน-ล่าง (2 ชุด) เช่น หลักสิบบนได้ [1,3] -> 13, 31
    if len(freq_digits) >= 2:
        two_digit_sets = [freq_digits[0] + freq_digits[1], freq_digits[1] + freq_digits[0]]
    elif len(freq_digits) == 1:
        two_digit_sets = [freq_digits[0] + freq_digits[0]]
    # สร้างสามตัวบน (2 ชุด) เช่น [1,3,5] -> 135, 531, ผสมเลขดับถ้ามี
    if len(freq_digits) >= 2 and dead_digits:
        three_digit_sets = [freq_digits[0] + freq_digits[1] + dead_digits[0], 
                            freq_digits[1] + freq_digits[0] + dead_digits[0]]
    elif len(freq_digits) >= 3:
        three_digit_sets = ["".join(freq_digits[:3]), "".join(freq_digits[::-1][:3])]
    else:
        three_digit_sets = []
else:
    # สูตร 2: ถ้าไม่มีเหตุการณ์เลขคู่/คี่
    explain_msg = "🔮 **สูตรอันดับ 2:** ไม่มีหลักใดที่เลขคู่/คี่ออกซ้ำ 3 งวด ใช้เลขถี่สุด 3 อันดับ"
    top3 = top3_freq_digits(draws)
    dead_digits = dead_digits_09(draws, n=5)
    # ผสมกับเลขดับ
    for d in dead_digits[:3]:
        if len(top3) >= 1:
            two_digit_sets.append(top3[0] + d)
        if len(top3) >= 2:
            two_digit_sets.append(top3[1] + d)
        if len(top3) >= 3:
            two_digit_sets.append(top3[2] + d)
        if len(two_digit_sets) >= 4:
            break
    # สามตัวบน 1 ชุด
    if len(top3) >= 3:
        three_digit_sets = [top3[0] + top3[1] + top3[2]]
    else:
        three_digit_sets = []

# ────────────────── DISPLAY RESULTS ──────────────────

st.subheader("📌 สรุปผลการวิเคราะห์และทำนาย")

st.markdown(explain_msg)

if eo_results:
    label, last_type, freq_list = eo_results[0]
    freq_digits = [str(x[0]) for x in freq_list if x[1] > 0]
    if last_type == "คู่":
        msg_type = f"หลัก**{label}** ออกเลขคู่ 3 งวดติด ทำนายว่างวดต่อไปควรเป็นเลข **คี่** ถี่สุด"
    else:
        msg_type = f"หลัก**{label}** ออกเลขคี่ 3 งวดติด ทำนายว่างวดต่อไปควรเป็นเลข **คู่** ถี่สุด"
    st.markdown(f"<div style='color:#2f4858;font-size:20px'>{msg_type}: <b>{', '.join(freq_digits)}</b></div>", unsafe_allow_html=True)

if two_digit_sets:
    st.markdown(f"**เลขสองตัวบน/ล่าง แนะนำ:** <span style='color:#C04000;font-size:24px'>{'  '.join(two_digit_sets[:2])}</span>", unsafe_allow_html=True)
if three_digit_sets:
    st.markdown(f"**เลขสามตัวบน แนะนำ:** <span style='color:#C04000;font-size:24px'>{'  '.join(three_digit_sets[:2])}</span>", unsafe_allow_html=True)

# ───── แสดงเลขดับ (0-9) ทั้งสามตัวบนและสองตัวล่างใน 5 งวดล่าสุด ─────
dead_digits = dead_digits_09(draws, n=5)
st.markdown(
    f"**เลขดับ (0-9 ที่ไม่ออกเลยใน 5 งวดล่าสุด ทั้งสามตัวบนและสองตัวล่าง):**<br>"
    f"<span style='color:#004080;font-size:22px'>{'  '.join(dead_digits) if dead_digits else '—'}</span>",
    unsafe_allow_html=True,
)

# ────────────────── FOOTER ──────────────────
st.caption("© 2025 YKLottaAI สูตรใหม่ (By ChatGPT)")
