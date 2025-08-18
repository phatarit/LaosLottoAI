# -*- coding: utf-8 -*-
"""
Lotto-like digit statistics & simple next-number suggester.

Assumptions:
- แต่ละงวดเป็นสตริง 4 หลัก "ABCD" มองเป็นสองส่วน: ('AB','CD').
- เอาเลขทุกหลักไปรวมกัน นับความถี่ 0–9 แบบรวมทุกตำแหน่ง
- ผลลัพธ์ (ฮิวริสติก):
  1) เลขเดี่ยว 1 ตัว = ตัวเลขที่มีความถี่รวมสูงสุด
  2) เลขสองตัว 4 ชุด = นำเลขเดี่ยวไปจับกับ 4 เลขที่ถี่รองลงมา (พยายามหลีกเลี่ยงเลข “ดับ” ช่วงหลัง)
  3) เลขสามตัว 1 ชุด = เลขเดี่ยว + สองเลขถัดไป
  4) เลขสี่ตัว 1 ชุด = เลขเดี่ยว + สามเลขถัดไป

หมายเหตุ: เป็นการทดลองเชิงสถิติ ไม่รับประกันผลลัพธ์จริง
"""

from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from typing import List, Tuple

# ────────────────────────── Data helpers ──────────────────────────

def parse_draws(raw: List[str]) -> List[Tuple[str, str]]:
    """
    แปลง "9767" -> ('97','67')
    ข้ามบรรทัดที่ไม่ใช่ตัวเลข 4 หลัก
    """
    out: List[Tuple[str, str]] = []
    for s in raw:
        s = s.strip()
        if len(s) == 4 and s.isdigit():
            out.append((s[:2], s[2:]))
    return out

def last_n(draws: List[Tuple[str, str]], n: int) -> List[Tuple[str, str]]:
    return draws[-n:] if n > 0 else []

def dead_digits_09(draws: List[Tuple[str, str]], n: int = 12) -> List[str]:
    """
    คืนเลข 0–9 ที่ “ไม่ปรากฏเลย” ใน n งวดหลังสุด (ทุกหลัก)
    """
    recent = last_n(draws, n)
    seen = set()
    for t, b in recent:
        seen.update(list(t))
        seen.update(list(b))
    return sorted(set("0123456789") - seen)

def digit_counter(draws: List[Tuple[str, str]]) -> Counter:
    c = Counter()
    for t, b in draws:
        c.update(list(t))
        c.update(list(b))
    return c

def top_k_digits(c: Counter, k: int, exclude: set | None = None) -> List[str]:
    exclude = exclude or set()
    items = [(d, cnt) for d, cnt in c.most_common() if d not in exclude]
    return [d for d, _ in items[:k]]

@dataclass
class Prediction:
    single_digit: str
    two_digit_sets: List[str]  # length 4
    three_digit: str
    four_digit: str

# ────────────────────────── Core heuristic ──────────────────────────

def predict_from_draws(draws: List[Tuple[str, str]], recent_n_for_dead: int = 12) -> Prediction:
    """
    เลือกเลขเดี่ยวจากความถี่รวมสูงสุด
    จับคู่เลขสองตัว 4 ชุดด้วยตัวที่ถี่รองลงมา โดยเรียง non-dead ก่อน dead
    สามตัว = เลขเดี่ยว + 2 ตัวถัดไป
    สี่ตัว = เลขเดี่ยว + 3 ตัวถัดไป
    """
    if not draws:
        raise ValueError("No draws provided")

    c = digit_counter(draws)
    dead = set(dead_digits_09(draws, n=recent_n_for_dead))

    # single digit
    single = c.most_common(1)[0][0]

    # เรียงผู้ท้าชิง (เว้น single) และให้ non-dead มาก่อน
    ordered = [d for d, _ in c.most_common() if d != single]
    non_dead = [d for d in ordered if d not in dead]
    dead_ones = [d for d in ordered if d in dead]
    partners = (non_dead + dead_ones)[:4]
    # กันกรณีข้อมูลน้อย เติมสำรอง
    while len(partners) < 4:
        for d in "0123456789":
            if d != single and d not in partners:
                partners.append(d)
            if len(partners) == 4:
                break

    # two-digit: single นำหน้า
    two_digit = [single + d for d in partners[:4]]

    # three/four digit
    p2 = (partners + [d for d in "0123456789" if d != single])
    three = single + p2[0] + p2[1]
    four  = single + p2[0] + p2[1] + p2[2]

    return Prediction(single_digit=single, two_digit_sets=two_digit, three_digit=three, four_digit=four)

# ────────────────────────── Pretty print ──────────────────────────

def summarize(draws: List[Tuple[str, str]], pred: Prediction, recent_n_for_dead: int = 12) -> str:
    c = digit_counter(draws)
    top5 = ", ".join([f"{d}:{cnt}" for d, cnt in c.most_common(5)])
    dead = " ".join(dead_digits_09(draws, recent_n_for_dead)) or "—"
    return (
        "=== STAT SUMMARY ===\n"
        f"Total draws: {len(draws)} (pairs)\n"
        f"Top-5 digits by frequency: {top5}\n"
        f"Dead digits (last {recent_n_for_dead}): {dead}\n\n"
        "=== SUGGESTION (Heuristic) ===\n"
        f"Single digit: {pred.single_digit}\n"
        f"Two-digit sets (4): {', '.join(pred.two_digit_sets)}\n"
        f"Three-digit: {pred.three_digit}\n"
        f"Four-digit: {pred.four_digit}\n"
    )

# ────────────────────────── Run as script ──────────────────────────
if __name__ == "__main__":
    # วางข้อมูลของคุณ (แต่ละบรรทัด = 4 หลักหนึ่งงวด) แทนที่บล็อกนี้
    RAW_DATA = """
    9767
    5319
    1961
    4765
    2633
    3565
    0460
    0619
    2059
    4973
    0155
    6446
    7947
    6774
    1193
    5976
    9256
    2433
    2624
    6314
    6872
    3553
    4268
    4594
    2234
    2114
    9307
    0704
    0607
    0295
    1605
    9766
    3922
    9695
    5720
    7993
    8927
    1148
    5597
    7041
    7028
    0610
    3717
    8053
    5263
    6322
    3811
    8521
    4077
    8649
    9846
    8573
    5487
    2572
    4667
    6835
    7922
    1556
    6895
    0318
    6569
    8723
    2952
    2935
    0516
    0982
    7341
    4870
    8066
    2229
    1835
    6671
    0908
    1339
    9824
    1034
    2588
    5720
    5878
    8932
    0390
    1350
    7001
    4605
    7809
    0536
    7135
    3116
    8715
    7433
    1697
    9344
    9003
    3061
    5803
    6480
    2529
    8233
    9899
    1717
    2034
    9138
    8831
    4299
    4700
    7372
    4706
    4826
    0210
    4010
    9862
    9629
    1976
    5800
    9264
    6026
    9248
    6273
    2007
    8487
    0480
    1222
    0924
    5402
    2224
    1828
    7939
    0879
    6254
    5514
    5473
    5551
    4264
    3910
    5508
    5288
    2499
    8246
    4186
    5468
    6189
    2232
    8186
    9024
    9922
    4354
    5767
    8785
    7095
    3873
    3675
    4475
    8391
    1724
    4254
    1226
    9528
    3099
    7380
    1622
    8499
    8932
    4413
    2263
    8368
    8251
    7215
    7243
    9390
    9938
    3890
    3772
    8596
    6118
    6727
    5915
    6478
    4856
    1857
    5488
    8302
    7706
    2858
    8258
    0911
    2420
    1596
    6804
    9545
    4389
    9432
    4271
    9490
    2552
    8721
    4351
    7999
    1269
    6619
    1155
    3598
    9902
    8717
    0147
    3710
    9057
    5419
    3303
    1399
    1493
    1732
    7206
    4883
    5059
    1209
    5459
    9106
    4248
    1619
    5514
    9036
    0072
    5056
    2878
    9018
    9065
    7076
    5941
    0517
    6143
    4324
    5048
    4075
    3664
    4005
    1150
    5402
    8431
    9284
    1274
    2076
    9698
    9359
    8254
    8224
    8239
    2764
    0605
    1157
    2846
    7339
    0667
    1647
    3866
    9865
    8644
    2703
    4596
    4821
    2811
    0489
    9636
    0040
    8435
    9692
    8919
    0079
    0741
    2989
    3362
    2002
    5177
    4614
    3851
    7589
    1786
    6347
    5269
    1433
    5136
    2810
    5575
    9497
    7162
    1480
    4493
    6353
    9036
    5457
    9318
    9498
    4601
    3741
    5092
    9285
    9989
    8667
    9265
    2256
    4609
    7449
    1393
    8733
    5381
    2944
    0086
    4361
    3205
    8524
    7970
    4277
    2897
    1810
    0055
    5774
    6045
    4647
    4176
    9681
    6705
    4528
    8994
    2439
    0411
    2160
    5215
    9842
    1177
    5480
    3164
    7289
    8459
    1626
    6845
    6647
    0609
    4445
    8159
    5795
    2011
    5116
    2499
    8112
    5741
    0702
    9591
    4409
    6279
    0827
    8518
    2532
    7985
    3794
    4091
    8789
    2597
    2146
    6374
    5284
    3119
    9626
    4464
    1737
    2033
    1630
    7743
    4822
    1056
    1126
    3228
    4787
    5673
    2206
    7957
    2066
    6234
    6988
    9130
    1037
    4269
    1942
    0440
    6849
    2528
    2872
    7617
    8242
    9473
    9503
    6683
    1934
    4662
    """.strip().splitlines()

    draws = parse_draws(RAW_DATA)
    pred  = predict_from_draws(draws, recent_n_for_dead=12)
    print(summarize(draws, pred, recent_n_for_dead=12))
