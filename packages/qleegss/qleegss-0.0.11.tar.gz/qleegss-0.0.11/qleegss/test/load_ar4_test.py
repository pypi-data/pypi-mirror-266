"""
load eeg mr4 data
"""
import numpy as np
from datetime import datetime
from scipy import signal


def load_eeg_ar4_one_night(eeg_path):
    # eeg data
    eeg_data = open(eeg_path, 'rb')
    eeg_len = len(eeg_data.read())
    eeg_data.seek(8, 0)
    length = int.from_bytes(eeg_data.read(4), byteorder='little', signed=False)
    eeg_data.seek(length, 0)
    all_package = np.array(list(eeg_data.read(eeg_len - length)))
    eeg_data.seek(21, 0)
    sample_count = int.from_bytes(eeg_data.read(4), byteorder='little', signed=False)
    eeg_data.seek(16, 0)
    point_bytes = int.from_bytes(eeg_data.read(1), byteorder='little', signed=False)
    channel_count = 4
    package_length = sample_count * point_bytes * channel_count + 18
    all_package = all_package.reshape(-1, package_length)
    all_package_data = all_package[:, 18:package_length]
    all_package_data = all_package_data.reshape(-1, point_bytes)
    all_package_data = all_package_data[:, 0] + all_package_data[:, 1] * 256
    raw_data = np.squeeze(all_package_data)
    data = np.transpose(raw_data.reshape(-1, channel_count))
    # ecg, emg, eeg0, eeg1
    data = signal.resample(data, int(data.shape[1]/5), axis=1)
    ecg = (data[0, :] - 32767) / 32767 * 2.0 * 1000 * 1000 / 192
    emg = (data[1, :] - 32767) / 32767 * 2.0 * 1000 * 1000 / 192
    eeg0 = (data[2, :] - 32767) / 32767 * 2.0 * 1000 * 1000 / 192
    eeg1 = (data[3, :] - 32767) / 32767 * 2.0 * 1000 * 1000 / 192
    # start time
    eeg_data.seek(33, 0)
    start_time = int.from_bytes(eeg_data.read(8), byteorder='little', signed=False) / 1000
    eeg_start_time = datetime.fromtimestamp(start_time)

    # end_time
    eeg_data.seek(41, 0)
    end_time = int.from_bytes(eeg_data.read(8), byteorder='little', signed=False) / 1000
    eeg_end_time = datetime.fromtimestamp(end_time)

    # 断连和丢包率
    disconnect_rate = 0
    package_loss_rate = 0

    # mac
    eeg_data.seek(49 + 32 + 5 * 4 + 33, 0)
    header_mac = eeg_data.read(65).decode('utf-8')[:12]  # 头贴mac

    eeg_data.seek(49 + 32 + 5 * 4 + 33 + 65 + 30 + 30 + 30 + 4 * 3 + 33, 0)
    box_mac = eeg_data.read(65).decode('utf-8')[:16]  # 基座mac

    eeg_data.close()
    return ecg, emg, eeg0, eeg1, eeg_start_time, eeg_end_time, disconnect_rate, package_loss_rate, header_mac, box_mac


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


if __name__ == '__main__':
    eeg_path_ = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\eeg.eeg'
    data_ = load_eeg_ar4_one_night(eeg_path_)
    print(data_[0].shape)
