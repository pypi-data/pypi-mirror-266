import numpy as np
import scipy.signal as signal


def load_eeg_one_epoch(data_bytes, data_split):
    eeg, eeg_package_id, acc, acc_package_id = x8_epoch_data_parser(data_bytes, data_split[0], data_split[1])
    eeg = (eeg[0, :] - 32767) / 32767 * 2.5 * 1000 * 1000 / 192
    if eeg.size == 500*30:
        eeg = signal.resample(eeg, 100 * 30)
    elif eeg.size == 500*15:
        eeg = signal.resample(eeg, 100 * 15)
    return eeg


def int_from_bytes_8bit(byte_arr):
    buffer = np.asarray(
        [1, 256, np.power(np.int64(256), 2), np.power(np.int64(256), 3), np.power(np.int64(256), 4),
         np.power(np.int64(256), 5), np.power(np.int64(256), 6), np.power(np.int64(256), 7)])

    res = byte_arr[0] * buffer[0] + byte_arr[1] * buffer[1] + byte_arr[2] * buffer[2] + byte_arr[3] * buffer[
        3] + byte_arr[4] * buffer[4] + byte_arr[5] * buffer[5] + byte_arr[6] * buffer[6] + byte_arr[7] * buffer[7]
    return np.sum(res)


def int_from_bytes_4bit(byte_arr):
    buffer = np.asarray([1, 256, np.power(np.int64(256), 2), np.power(np.int64(256), 3)])

    res = byte_arr[0] * buffer[0] + byte_arr[1] * buffer[1] + byte_arr[2] * buffer[2] + byte_arr[3] * buffer[3]
    return np.sum(res)


def x8_epoch_data_parser(bytes_arr, eeg_length, acc_length):
    eeg_bytes = bytes_arr[0: + eeg_length]
    eeg, eeg_package_id = x8_epoch_eeg_or_acc_parser(eeg_bytes, 50, 2, 2)
    acc_bytes = bytes_arr[eeg_length:eeg_length + acc_length]
    acc, acc_package_id = x8_epoch_eeg_or_acc_parser(acc_bytes, 5, 2, 3)
    return eeg, eeg_package_id, acc, acc_package_id


def x8_epoch_eeg_or_acc_parser(eeg_or_acc_bytes, sample_count, point_bytes, channel_count):
    all_packages = np.array(eeg_or_acc_bytes)
    package_length = sample_count * point_bytes * channel_count + 18
    all_packages = all_packages.reshape(-1, package_length)

    all_package_id = all_packages[:, 10:14]
    all_package_data = all_packages[:, 18:package_length]

    all_package_id = all_package_id.astype(np.uint8)
    all_package_id = np.apply_along_axis(int_from_bytes_4bit, axis=1, arr=all_package_id)
    all_package_id = all_package_id.astype(np.int32)

    all_package_data = all_package_data.reshape(-1, point_bytes)
    all_package_data = all_package_data[:, 0] + all_package_data[:, 1] * 256

    data_total = all_package_data
    data_total = data_total[0:len(data_total) // channel_count * channel_count]
    data_total_T = data_total.reshape(-1, channel_count)
    data_total = []
    for i in range(channel_count):
        data_total.append(data_total_T[:, i])
    data_total = np.asarray(data_total)
    return data_total, all_package_id
