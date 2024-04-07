import numpy as np
from datetime import timedelta
import matplotlib.dates as mdates


def plot_acc(ax, acc, start_time):
    sf = 50
    win = 15

    diff_acc = np.abs(acc[:, 1:] - acc[:, 0:-1])
    diff_acc = np.c_[diff_acc, [0, 0, 0]]

    avg_diff_acc = np.sum(np.reshape(np.sum(diff_acc, axis=0), [-1, sf * win]), axis=1) / (sf * win)
    # set max diff acc to 500
    avg_diff_acc[avg_diff_acc > 500] = 500
    data_length = avg_diff_acc.shape[0]

    t = np.arange(data_length) * win / 3600
    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)
    ax.plot(timestamp_num, avg_diff_acc, lw=1.5, color='r')

    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_ylabel("Head Movement", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(timestamp[0], timestamp[-1])