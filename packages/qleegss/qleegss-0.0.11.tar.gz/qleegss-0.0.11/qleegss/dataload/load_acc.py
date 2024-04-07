"""
加载acc数据
"""
import numpy as np


def load_acc(acc_path):
    channel_count = 3
    with open(acc_path, 'rb') as acc_data:
        acc_data.seek(8, 0)
        length = int.from_bytes(acc_data.read(4), byteorder='little', signed=False)
        acc_data.seek(16, 0)
        point_bytes = int.from_bytes(acc_data.read(1), byteorder='little', signed=False)
        acc_data.seek(21, 0)
        sample_count = int.from_bytes(acc_data.read(4), byteorder='little', signed=False)

    with open(acc_path, 'rb') as f:
        byte_data = f.read()

    all_package = np.frombuffer(byte_data, dtype=np.uint8)[length:]
    del byte_data
    package_length = sample_count * point_bytes * channel_count + 18
    all_package = all_package.reshape(-1, package_length)[:, 18:package_length].reshape(-1, point_bytes)
    all_package_data = all_package[:, 0] + all_package[:, 1] * 256
    del all_package
    raw_data = np.squeeze(all_package_data)
    del all_package_data
    data = np.transpose(raw_data.reshape(-1, channel_count)).astype(np.int32)
    acc = data - 32767
    del data

    return acc


if __name__ == '__main__':
    acc_path_ = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\acc.acc'
    data_ = load_acc(acc_path_)
    print(data_[0].shape)
