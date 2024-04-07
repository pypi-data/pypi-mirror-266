import scipy.signal as signal


def eeg_acc_reshape(acc, eeg=None):
    acc = acc[:, : (acc.shape[1] // (15 * 50)) * (15 * 50)]
    if eeg is not None:
        eeg = eeg[:int(eeg.shape[0] / (30 * 500)) * (30 * 500)].reshape(-1, 30 * 500)
        eeg = signal.resample(eeg, 100 * 30, axis=1).ravel()
    return acc, eeg

