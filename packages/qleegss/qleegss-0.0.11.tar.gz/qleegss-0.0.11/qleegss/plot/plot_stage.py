"""
绘制分期图
"""
import matplotlib.pyplot as plt
from qleegss.plot.plot_eeg_spectrogram import plot_spectrogram
import numpy as np
from datetime import timedelta, datetime
import matplotlib.dates as mdates
from scipy.signal import savgol_filter
from qleegss.plot.plot_acc import plot_acc


def plot_stage(eeg, eeg_start_time, sf_eeg, eeg_path, acc, stage_res, use_map_dict=True):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(20, 4 * 4))
    # spectrogram
    t = plot_spectrogram(ax1, eeg, eeg_start_time, sf_eeg)
    # acc
    plot_acc(ax2, acc, eeg_start_time)
    # posture
    plot_sleep_posture(ax3, sleep_posture_analyse(acc), eeg_start_time)
    # stage
    plot_stage_res(ax4, stage_res, eeg_start_time, use_map_dict)

    # config
    plt.tight_layout()
    save_path = eeg_path.replace('eeg.eeg', 'sleep_fig.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close('all')


def plot_sleep_posture(ax, grade, start_time):
    sf = 50
    # assert grade.shape[0] == 1, "The grade of head bias should be a 1-D ndarray"
    t = np.arange(grade.shape[0]) / sf / 3600
    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)
    ax.plot(timestamp_num, grade, lw=1.5, color='b')
    ax.set_ylim(-3.5, 3.5)
    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_yticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    ax.set_yticklabels(['Sleep Face Down', 'Lie on the Left', 'Lie Flat', 'Lie on the Right', 'Sleep Face Down'], )
    ax.set_ylabel("Sleep Postures", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})
    ax.grid(visible=True, axis='y', linewidth=0.5)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(timestamp[0], timestamp[-1])


def sleep_posture_analyse(acc):
    acc_y = acc[1, :]
    acc_z = acc[2, :]

    cos = acc_z / (np.sqrt(acc_z * acc_z + acc_y * acc_y))
    upper_grade = np.arccos(cos)
    grade = upper_grade * (acc_y / (np.abs(acc_y)+1e-16))
    grade = savgol_filter(grade, window_length=50, polyorder=1)

    return grade


def plot_stage_res(ax, hypno, start_time, use_map_dict=True):
    win = 30

    t = np.arange(hypno.size) * win / 3600
    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)

    map_dict = {
        3: 0,
        2: 1,
        1: 2,
        4: 3,
        0: 4,
        5: 5
    }
    #
    hypno = [map_dict.get(x, x) for x in hypno] if use_map_dict else hypno

    n3_sleep = np.ma.masked_not_equal(hypno, 0)
    n2_sleep = np.ma.masked_not_equal(hypno, 1)
    n1_sleep = np.ma.masked_not_equal(hypno, 2)
    rem_sleep = np.ma.masked_not_equal(hypno, 3)
    wake = np.ma.masked_not_equal(hypno, 4)
    abnormal = np.ma.masked_not_equal(hypno, 5)

    ax.plot(timestamp_num, hypno, lw=2, color='k')
    ax.plot(timestamp_num, abnormal, lw=2, color='k')
    ax.plot(timestamp_num, wake, lw=2, color='orange')
    ax.plot(timestamp_num, rem_sleep, lw=2, color='lime')
    ax.plot(timestamp_num, n1_sleep, lw=2, color='yellowgreen')
    ax.plot(timestamp_num, n2_sleep, lw=2, color='deepskyblue')
    ax.plot(timestamp_num, n3_sleep, lw=2, color='royalblue')

    ax.set_ylim([-0.1, 5.8])
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_yticklabels(['N3 Sleep', 'N2 Sleep', 'N1 Sleep', 'REM Sleep', 'Wake', 'Abnormal'], )
    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_ylabel("Sleep Staging Result", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim([timestamp_num[0], timestamp_num[-1]])


if __name__ == '__main__':
    eeg_ = np.random.rand(30000)
    acc_ = np.random.rand(3, 30000)
    stage_res_ = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    plot_stage(eeg_, datetime.now(), 100, './eeg.eeg', acc_, stage_res_)
    plt.show()
