"""
计算睡眠变量
"""
import numpy as np
import pandas as pd


def sl_waso_ar(hypno):
    sl = hypno.size
    gu_ = hypno.size
    hypno_mask = hypno != 0
    # 找连续10个epoch睡着的
    for i in range(hypno_mask.size):
        if np.sum(hypno_mask[i:i+10]) == 10:
            sl = i
            break
    # 从后找睡着的
    hypno_mask = hypno_mask[::-1]
    for j in range(hypno_mask.size):
        if np.sum(hypno_mask[j:j+1]) == 1:
            gu_ = hypno.size - j
            break
    # 睡与醒之间的清醒
    sleep_hypno= hypno[sl:gu_]
    sleep_hypno_mask = sleep_hypno == 0
    waso = np.sum(sleep_hypno_mask)
    # 清醒次数
    arr = sleep_hypno_mask
    merged_arr = [arr[0]]
    for i in range(1, len(arr)):
        if arr[i] != arr[i - 1]:
            merged_arr.append(arr[i])
    ar = np.sum(merged_arr)

    return sl, waso, ar


def sleep_metrics(eeg_path, hypno):
    # 总记录时间
    trt = hypno.shape[0]
    # 总睡眠时间
    tst = sum(1 for num in hypno if num in [1, 2, 3, 4]) if np.sum(hypno) > 0 else 0
    # 睡眠效率
    se = np.sum(hypno[hypno != 5] != 0) / hypno.size
    # 入睡后清醒时间， 入睡后清醒次数
    sol, waso, ar = sl_waso_ar(hypno) if tst > 10 else (0, 0, 0)

    n1 = np.sum(hypno == 1)
    n2 = np.sum(hypno == 2)
    n3 = np.sum(hypno == 3)
    rem = np.sum(hypno == 4)
    # save
    df = {
        "TRH(H)": [trt*30/3600],
        "TST(H)": [tst*30/3600],
        "SE(%)": [se*100],
        "SOL(H)": [sol*30/3600],
        "WASO(M)": [waso*30/3600],
        "AR": [ar],
        "Hypno": [hypno]
    }
    df = pd.DataFrame(df)
    save_path = eeg_path.replace('eeg.eeg', "analysis_results.xlsx")
    with pd.ExcelWriter(save_path) as writer:
        df.to_excel(writer, sheet_name='sleep variables')
    return trt, tst, se, sol, waso, ar, n1, n2, n3, rem


if __name__ == '__main__':
    hypno_ = np.array([0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 0, 1, 0, 1, 0])
    trt_, tst_, se_, sol_, waso_, ar_, n1_, n2_, n3_, rem_ = sleep_metrics('eeg.eeg', hypno_)
    print(trt_, tst_, se_, sol_, waso_, ar_, n1_, n2_, n3_, rem_)
