import matplotlib.pyplot as plt
from lspopt import spectrogram_lspopt
import numpy as np
import matplotlib.dates as mdates
from datetime import timedelta, datetime
from matplotlib.colors import Normalize


def plot_spectrogram(ax, eeg, eeg_start_time, sf_eeg):
    sf = sf_eeg
    win_sample = int(30 * sf)
    assert eeg.size > 2 * win_sample, "`data` length must be at least 2 * `30`."
    f, t, Sxx = spectrogram_lspopt(eeg, sf, nperseg=win_sample, noverlap=0)
    t /= 3600
    timestamp = [eeg_start_time + timedelta(hours=hours) for hours in t]
    timestamp = mdates.date2num(timestamp)
    Sxx = 10 * np.log10(Sxx)  # Convert uV^2 / Hz --> dB / Hz

    v_min, v_max = np.percentile(Sxx, [0 + 5, 100 - 5])
    norm = Normalize(vmin=v_min, vmax=v_max)
    ax.pcolormesh(timestamp, f, Sxx, norm=norm, cmap='Spectral_r', antialiased=True, shading="auto")
    ax.xaxis_date()
    ax.set_ylim([0, 50])
    ax.set_yticks([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])

    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_ylabel("Frequency [Hz]", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    return t


if __name__ == '__main__':
    eeg_ = np.random.rand(30000)
    fig, ax1 = plt.subplots(nrows=1, figsize=(12, 5))
    t_ = plot_spectrogram(ax1, eeg_, datetime.now(), 100)
    plt.show()
