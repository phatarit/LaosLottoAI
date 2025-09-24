# app.py
# -*- coding: utf-8 -*-
import random
import streamlit as st
from collections import Counter

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด",
    page_icon="icon.png",
    layout="centered"
)

# ---------------- Styles (White bg / Blue frame / Red numbers) ----------------
st.markdown("""
<style>
.stApp { background:#ffffff; color:#111; }
.block-container{ max-width:820px; }
h1.title-blue{
  color:#0b5ed7; margin:10px 0 18px 0; font-weight:800;
}
.frame{
  border:2px solid #0b5ed7; border-radius:14px; padding:14px 16px; margin:10px 0 18px 0;
  background:#f8fbff;
}
.tag{ display:inline-block; color:#0b5ed7; font-weight:800; margin-right:10px; font-size:1.15rem;}
.num-big{ color:#d90429; font-weight:900; line-height:1; }
.num-xl{ font-size:64px; }    /* ข้อ 1 ใหญ่สุด */
.num-lg{ font-size:42px; }    /* ข้อ 2,3 */
.num-md{ font-size:36px; }    /* ข้อ 4 */
.inp{
  background:#fff;border:1.5px solid #c9d7ff;border-radius:10px;padding:10px 12px;
}
.btn > button{
  background:#0b5ed7 !important;color:#fff !important;border:none !important;
  border-radius:10px !important;padding:8px 14px !important;font-weight:700 !important;
}
.help{ color:#5f6b7a; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title-blue">Lao Lotto วางเลข 4 หลัก ทีละบรรทัด 5 งวด</h1>', unsafe_allow_html=True)

# ---------------- Input ----------------
DEFAULT = "8775\n3798\n6828\n0543\n0862"  # ตัวอย่าง 5 งวด
raw = st.text_area("วางเลข 4 หลัก (5 งวด, ทีละบรรทัด)", value=DEFAULT, height=130, help="ตัวอย่าง: 8775\\n3798\\n6828\\n0543\\n0862", key="inp")
colb1, colb2 = st.columns([1,1])
with colb1:
    rnd_btn = st.button("สุ่มใหม่ผล (ข้อ 2–4)", key="reroll", help="สุ่มชุดที่แสดงใหม่ตามเงื่อนไขเดิม", type="primary", use_container_width=True)
with colb2:
    st.write("")  # spacer

def parse_5(raw_text:str):
    lines = [s.strip() for s in raw_text.splitlines() if s.strip()]
    # เก็บเฉพาะตัวเลข 4 หลัก และเอาเฉพาะ 5 รายการสุดท้าย
    nums = [s for s in lines if len(s)==4 and s.isdigit()][-5:]
    return nums

nums = parse_5(raw)
if len(nums) < 5:
    st.markdown('<div class="help">กรุณาวางเลข 4 หลักให้ครบ 5 งวด</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- Core helpers ----------------
def digits(s): return [c for c in s]  # 4 ตัวอักษร
def tens(s):   return s[2]            # หลักสิบ (C)
def ones(s):   return s[3]            # หลักหน่วย (D)
def thousands(s): return s[0]         # หลักพัน (A)

# 1) เด่น: จากงวดที่ 3 (ตัวที่ index 2 ของลิสต์ 5 งวด)
third = nums[2]
hot_pair = [tens(third), ones(third)]  # 2 และ 8 ในตัวอย่าง
hot_pair_unique = []
for d in hot_pair:
    if d not in hot_pair_unique:
        hot_pair_unique.append(d)

# 2) เจาะ: ใช้เลขจากข้อ 1 ไปจับกับ "หลักสิบ" ของ 3 งวดล่าสุด (nums[-3:], ล่าสุดสุดอยู่ท้าย)
special_set = set(list("456210"))
recent3 = nums[-3:]
tens_recent = [tens(x) for x in recent3]  # ได้เลขหลักสิบของสามงวดล่าสุด
pairs_all = []
for h in hot_pair_unique:
    for t in tens_recent:
        pair = h + t
        if pair not in pairs_all:
            pairs_all.append(pair)

# คัดเฉพาะคู่ที่หลักที่สองอยู่ใน special_set
pairs_filtered = [p for p in pairs_all if p[1] in special_set]
if not pairs_filtered:
    # ถ้าไม่มีคู่อะไรผ่าน filter ให้ใช้ pairs_all แทน
    pairs_filtered = pairs_all[:]

# สุ่ม 5 ชุด (ถ้าน้อยกว่าก็แสดงเท่าที่มี)
random.seed(None)  # ใช้ seed ตามเวลา
pairs_show = random.sample(pairs_filtered, k=min(5, len(pairs_filtered)))

# 3) เน้น: หาเลขที่ "หายไป" จาก 5 งวดล่าสุด แล้วนำมาใส่เป็นหลักหน้า
all_digits = set("0123456789")
seen = set("".join(nums))
missing = sorted(list(all_digits - seen), key=lambda x:int(x))
if missing:
    prefix = missing[0]   # ใช้ตัวเล็กสุดเพื่อเสถียร
else:
    # ถ้าไม่มีเลขหาย เลือกตัวที่พบน้อยสุดแทน
    cnt = Counter("".join(nums))
    minc = min(cnt.values())
    cands = sorted([d for d,c in cnt.items() if c==minc], key=lambda x:int(x))
    prefix = cands[0]

triples_show = [prefix + p for p in pairs_show]  # ใส่ด้านหน้า

# 4) รวย: เลือกหนึ่งชุดจากข้อ 3 แบบสุ่ม แล้วนำ "หลักพัน" ของงวดล่าสุดมาเติมหน้า
pick3 = random.choice(triples_show)
thou = thousands(nums[-1])   # หลักพันของงวดล่าสุด
four_show = thou + pick3

# ---------------- Display (only labels & numbers) ----------------
# ข้อ 1: เด่น (ใหญ่สุด)
st.markdown('<div class="frame"><span class="tag">เด่น</span><span class="num-big num-xl">{}</span></div>'.format(" ".join(hot_pair_unique)), unsafe_allow_html=True)

# ข้อ 2: เจาะ
st.markdown('<div class="frame"><span class="tag">เจาะ</span><span class="num-big num-lg">{}</span></div>'.format(", ".join(pairs_show)), unsafe_allow_html=True)

# ข้อ 3: เน้น
st.markdown('<div class="frame"><span class="tag">เน้น</span><span class="num-big num-lg">{}</span></div>'.format(", ".join(triples_show)), unsafe_allow_html=True)

# ข้อ 4: รวย (1 ชุด)
st.markdown('<div class="frame"><span class="tag">รวย</span><span class="num-big num-md">{}</span></div>'.format(four_show), unsafe_allow_html=True)

st.caption("หมายเหตุ: รูปแบบตามเงื่อนไขที่ระบุ — สุ่มเฉพาะข้อ 2 และ 4 (เปลี่ยนผลได้ด้วยปุ่ม “สุ่มใหม่ผล”).")
