import scipy.signal as signal


def eeg_acc_reshape(acc, *args):
    # 直接在原始数据上进行操作，不创建新的数组
    acc = acc[:, : acc.shape[1] // (15 * 50) * (15 * 50)]

    # 使用列表推导式和切片来进行原地操作
    eeg_reshaped = [
        signal.resample(eeg[:eeg.shape[0] // (30 * 500) * (30 * 500)].reshape(-1, 30 * 500), 100 * 30, axis=1).ravel()
        for eeg in args]

    # 返回结果，使用解包来返回多个值
    return acc, *eeg_reshaped


def ecg_emg_reshape(ecg, emg):
    ecg = signal.resample(ecg[:ecg.shape[0] // (30 * 500) * (30 * 500)].reshape(-1, 30 * 500), 10 * 30, axis=1).ravel()
    emg = signal.resample(emg[:emg.shape[0] // (30 * 500) * (30 * 500)].reshape(-1, 30 * 500), 10 * 30, axis=1).ravel()

    # 返回结果，使用解包来返回多个值
    return ecg, emg
