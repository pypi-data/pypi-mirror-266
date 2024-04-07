"""
绘制慢波增强对比图
"""
import matplotlib
import matplotlib.pyplot as plt
from qleegss.plot.plot_eeg_spectrogram import plot_spectrogram
import numpy as np
import matplotlib.dates as mdates
from datetime import timedelta, datetime
import scipy.signal as signal


def plot_sw(eeg, eeg_start_time, sf_eeg, eeg_path, idx):
    idx = idx[:(idx.size // 2) * 2]
    stim_idx = idx[0::2]
    sham_idx = idx[1::2]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 5 + 2 + 10))
    # spectrogram
    t = plot_spectrogram(ax1, eeg, eeg_start_time, sf_eeg)

    # point
    plot_point(ax2, t, eeg_start_time, stim_points=stim_idx, sham_points=sham_idx)

    # sw
    plot_wave(ax3, eeg, sf_eeg, stim_idx, sham_idx)
    # save
    save_path = eeg_path.replace('eeg.eeg', 'sw_stim_sham_fig.png')
    fig.suptitle('STIM & SHAM', fontsize=25)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close('all')


def plot_point(ax, t, start_time, stim_points=None, sham_points=None):
    stim_points = stim_points / 100.0 / 3600
    sham_points = sham_points / 100.0 / 3600

    stim_points_timestamp = [start_time + timedelta(hours=hours) for hours in stim_points]
    stim_points_timestamp_num = mdates.date2num(stim_points_timestamp)

    sham_points_timestamp = [start_time + timedelta(hours=hours) for hours in sham_points]
    sham_points_timestamp_num = mdates.date2num(sham_points_timestamp)

    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)

    ax.scatter(stim_points_timestamp_num, np.ones(len(stim_points)) * 15, c="red")
    ax.scatter(sham_points_timestamp_num, np.ones(len(stim_points)) * 5, c="gray")

    ax.set_ylim([0, 20])
    ax.set_yticks([5, 15])
    ax.set_yticklabels(["Sham", "Stim"])

    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(timestamp_num[0], timestamp_num[-1])

    return ax


def plot_wave(ax, eeg, sf_eeg, stim_indicator, sham_indicator):
    eeg_filtered = eeg_filter(eeg, sf_eeg, 0.5, 3)

    seg_downlim = 1  # ERP down limitation
    seg_uplim = 4  # ERP up limitation

    EEGT = {'stim': np.array(
        [eeg_filtered[i - int(sf_eeg * seg_downlim):i + int(sf_eeg * seg_uplim)] for i in
         stim_indicator]),
        'sham': np.array(
            [eeg_filtered[i - int(sf_eeg * seg_downlim):i + int(sf_eeg * seg_uplim)] for i in
             sham_indicator])}

    stim_sem = np.std(EEGT['stim'], axis=0) / np.sqrt(len(EEGT['stim']) / 2)
    sham_sem = np.std(EEGT['sham'], axis=0) / np.sqrt(len(EEGT['sham']) / 2)

    t = np.arange(-100, 400) / sf_eeg
    eeg_stim_mean: object = np.mean(EEGT['stim'], axis=0)
    eeg_sham_mean = np.mean(EEGT['sham'], axis=0)

    ax.errorbar(t, eeg_stim_mean, yerr=stim_sem, label='STIM', alpha=0.1, color='r')

    ax.errorbar(t, eeg_sham_mean, yerr=sham_sem, label='SHAM', alpha=0.1, color='k')

    onset_idx = 100
    offset_idx = int(onset_idx + 1.075 * sf_eeg)
    ax.scatter(t[[onset_idx, offset_idx]], eeg_stim_mean[[onset_idx, offset_idx]], c='r',
               label='STIM Timings')
    ax.scatter(t[[onset_idx, offset_idx]], eeg_sham_mean[[onset_idx, offset_idx]], c='g',
               label='SHAM Timings')

    ax.set_xlim([min(t), max(t)])

    ax.set_xlabel('Time (s)', fontsize=25)
    ax.set_ylabel('Voltage (uV)', fontsize=25)
    ax.tick_params(labelsize=25)
    ax.legend(fontsize=20, loc='upper right')


def eeg_filter(eeg, sf_eeg, highpass, lowpass):
    wn_h = 2 * highpass / sf_eeg
    b_h, a_h = signal.butter(3, wn_h, 'highpass', analog=False)

    eeg = signal.lfilter(b_h, a_h, eeg)
    wn_l = 2 * lowpass / sf_eeg
    b_l, a_l = signal.butter(3, wn_l, 'lowpass', analog=False)

    eeg = signal.lfilter(b_l, a_l, eeg)

    return eeg


if __name__ == '__main__':
    eeg_ = np.random.rand(30000)
    idx_ = np.array([10000, 10100, 20000, 20100])
    plot_sw(eeg_, datetime.now(), 100, './eeg.eeg', idx_)
    plt.show()
