"""
计算刺激个数和翻身次数
"""
import numpy as np


def count_turnover(acc, win=30, sf=50):

    diff_acc = np.abs(acc[:, 1:] - acc[:, 0:-1])
    diff_acc = np.c_[diff_acc, [0, 0, 0]]

    avg_diff_acc = np.sum(np.reshape(np.sum(diff_acc, axis=0), [-1, sf * win]), axis=1) / (sf * win)
    # set max diff acc to 500
    avg_diff_acc[avg_diff_acc > 500] = 500
    normal_state = 100

    turnover = np.where(avg_diff_acc > normal_state)[0].shape[0]
    return turnover
