from scipy.io import savemat
from datetime import datetime
import numpy as np


def save_x8_to_mat(eeg_path, eeg, acc, start_time):
    # 将datetime对象转换为POSIX时间戳
    posix_timestamp = np.datetime64(start_time).astype('float') / 1e9
    mat_path = eeg_path.replace('eeg.eeg', 'eeg_and_acc.mat')
    savemat(mat_path, {'eeg': eeg, 'acc': acc, 'start_time': posix_timestamp})


def save_mr_to_mat(eeg_path, eeg0, eeg1, acc, start_time, ecg=None, emg=None):
    posix_timestamp = np.datetime64(start_time).astype('float') / 1e9
    mat_path = eeg_path.replace('eeg.eeg', 'eeg_and_acc.mat')
    data_to_save = {'eeg0': eeg0, 'eeg1': eeg1, 'acc': acc, 'start_time': posix_timestamp}
    if ecg is not None:
        data_to_save['ecg'] = ecg
    if emg is not None:
        data_to_save['emg'] = emg
    savemat(mat_path, data_to_save)
