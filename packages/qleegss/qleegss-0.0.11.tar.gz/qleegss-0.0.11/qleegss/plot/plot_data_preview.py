"""
绘制数据预览
"""
from qleegss.plot.plot_acc import plot_acc
import matplotlib.pyplot as plt
from qleegss.plot.plot_eeg_spectrogram import plot_spectrogram
import numpy as np
import matplotlib.dates as mdates
from datetime import timedelta


def plot_preview_mr4(eeg0, eeg1, ecg, emg, acc, eeg_start_time, sf_eeg, eeg_path):
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(20, 5 * 4))
    # spectrogram
    t = plot_spectrogram(ax1, eeg0, eeg_start_time, sf_eeg)
    t = plot_spectrogram(ax2, eeg1, eeg_start_time, sf_eeg)
    # ecg
    plot_ecg(ax3, ecg, eeg_start_time)
    # emg
    plot_emg(ax4, emg, eeg_start_time)
    # acc
    plot_acc(ax5, acc, eeg_start_time)

    # config
    plt.tight_layout()
    save_path = eeg_path.replace('eeg.eeg', 'data_preview.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close('all')


def plot_preview_mr2(eeg0, eeg1, acc, eeg_start_time, sf_eeg, eeg_path):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 3 * 4))
    # spectrogram
    t = plot_spectrogram(ax1, eeg0, eeg_start_time, sf_eeg)
    t = plot_spectrogram(ax2, eeg1, eeg_start_time, sf_eeg)
    # acc
    plot_acc(ax3, acc, eeg_start_time)

    # config
    plt.tight_layout()
    save_path = eeg_path.replace('eeg.eeg', 'data_preview.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close('all')


def plot_ecg(ax, ecg, start_time):

    sf = 100
    time_per_sample = 1 / sf / 3600
    t = np.arange(ecg.shape[0]) * time_per_sample
    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)
    ax.plot(timestamp_num, ecg, lw=1.5, color='r')

    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_ylabel("ECG [μV]", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})

    ax.set_ylim(-100, 100)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(timestamp[0], timestamp[-1])


def plot_emg(ax, emg, start_time):

    sf = 100

    time_per_sample = 1 / sf / 3600
    t = np.arange(emg.shape[0]) * time_per_sample
    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)
    ax.plot(timestamp_num, emg, lw=1.5, color='r')

    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_ylabel("EMG [μV]", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})

    # 设置y轴的显示范围
    ax.set_ylim(-500, 500)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(timestamp[0], timestamp[-1])
