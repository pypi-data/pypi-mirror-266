from qleegss.dataload.load_eeg_x8_one_night import load_eeg_x8_one_night
from qleegss.dataload.load_acc import load_acc
from qleegss.dataload.load_sti import load_sti
from qleegss.model.predict import predict_one_trail
from qleegss.plot.plot_sw import plot_sw
from qleegss.plot.plot_stage import plot_stage
from qleegss.other.metric import sleep_metrics
from qleegss.pdf.sleep_report import generate_sleep_report
import logging
from qleegss.dataload.load_device_type import load_device_type
from qleegss.dataload.load_eeg_ar4_one_night import load_eeg_ar4_one_night
from qleegss.plot.plot_data_preview import plot_preview_mr4
from qleegss.pdf.data_preview import generate_data_preview
from qleegss.dataload.load_eeg_ar2_one_night import load_eeg_ar2_one_night
from qleegss.plot.plot_data_preview import plot_preview_mr2
from qleegss.other.save_mat import save_x8_to_mat, save_mr_to_mat
from qleegss.other.eeg_acc_reshape import eeg_acc_reshape


class DataHandler:
    def __init__(self, eeg_path_p=None, acc_path_p=None, sti_path_p=None):
        self.eeg = None
        self.start_time = None
        self.eeg_path = eeg_path_p
        self.sf_eeg = 100
        self.acc = None
        self.acc_path = acc_path_p
        self.sti = None
        self.sti_path = sti_path_p
        self.stage_result = None
        self.phone = None
        self.name = None
        self.end_time = None
        self.disconnect_rate = None
        self.package_loss_rate = None
        self.device = None
        self.ecg = None
        self.emg = None
        self.eeg0 = None
        self.eeg1 = None
        self.header_mac = None
        self.box_mac = None

    def load_eeg_x8_one_night(self):
        self.eeg, self.start_time, self.end_time,  self.disconnect_rate, self.package_loss_rate = \
            load_eeg_x8_one_night(self.eeg_path)

    def load_eeg_ar4_one_night(self):
        self.ecg, self.emg, self.eeg0, self.eeg1, self.start_time, self.end_time, self.disconnect_rate, \
            self.package_loss_rate, self.header_mac, self.box_mac = load_eeg_ar4_one_night(self.eeg_path)

    def load_eeg_ar2_one_night(self):
        self.eeg0, self.eeg1, self.start_time, self.end_time, self.disconnect_rate, self.package_loss_rate, \
            self.header_mac, self.box_mac = load_eeg_ar2_one_night(self.eeg_path)

    def load_acc(self):
        self.acc = load_acc(self.acc_path)

    def load_sti(self):
        self.sti = load_sti(self.sti_path)

    def load_device_type(self):
        self.device = load_device_type(self.eeg_path)

    def save_mat(self):
        if self.device == 101:
            save_x8_to_mat(self.eeg_path, self.eeg, self.acc, self.start_time)
        elif self.device == 102 or self.device == 44:
            save_mr_to_mat(self.eeg_path, self.eeg0, self.eeg1,  self.acc, self.start_time, self.ecg, self.emg)
        else:
            pass

    def eeg_acc_reshape(self):
        self.acc, self.eeg = eeg_acc_reshape(self.acc, self.eeg)

    def sleep_stage(self):
        self.stage_result = predict_one_trail(self.eeg)

    def clear_eeg(self):
        self.eeg = None

    def clear_acc(self):
        self.acc = None

    def clear_sti(self):
        self.sti = None

    def clear_mr_data(self):
        self.ecg = None
        self.emg = None
        self.eeg0 = None
        self.eeg1 = None


if __name__ == '__main__':
    logging.basicConfig(filename='example.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    eeg_path = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\eeg.eeg'
    acc_path = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\acc.acc'
    sti_path = None
    try:
        data = DataHandler(eeg_path, acc_path, sti_path)
        data.load_device_type()

        if data.device == 101:
            logging.info('--------- X8 device ---------')
            data.load_eeg_x8_one_night() if data.eeg_path is not None else None
            data.load_acc() if data.acc_path is not None else None
            data.load_sti() if data.sti_path is not None else None
            logging.info('load data success.')

            # 保存mat
            data.save_mat()
            logging.info('save data to mat success.')

            # 重采样
            data.eeg_acc_reshape()
            logging.info('down sample success.')

            # 慢波图绘制
            plot_sw(data.eeg, data.start_time, data.sf_eeg, data.eeg_path, data.sti) if data.sti is not None else None
            logging.info('slow wave success.')

            # 清除sti
            data.clear_sti()

            # 生成分期
            data.sleep_stage()
            logging.info('sleep stage success.')

            # 绘制分期
            plot_stage(data.eeg, data.start_time, data.sf_eeg, data.eeg_path, data.acc, data.stage_result)
            logging.info('plot stage success.')

            # 清数据
            data.clear_eeg()
            data.clear_acc()

            # 计算睡眠指标&保存成excel
            sleep_metrics(data.eeg_path, data.stage_result)
            logging.info('save xlsx success.')

            # pdf
            generate_sleep_report(data)
            logging.info('save report success.')

        # 4通道小鼠
        elif data.device == 102:
            logging.info('--------- MR4 device ---------')
            # 加载数据
            data.load_eeg_ar4_one_night() if data.eeg_path is not None else None
            data.load_acc() if data.acc_path is not None else None
            logging.info('load data success.')
            # 保存mat
            data.save_mat()
            logging.info('save data to mat success.')
            # 重采样
            data.eeg_acc_reshape()
            logging.info('down sample success.')
            # data preview
            plot_preview_mr4(data.eeg0, data.eeg1, data.ecg, data.emg, data.acc, data.start_time, data.sf_eeg, data.eeg_path)
            logging.info('plot data success.')
            data.clear_mr_data()
            # save pdf
            generate_data_preview(data)
            logging.info('save data preview success.')

        # 2通道小鼠
        elif data.device == 44:
            logging.info('--------- MR2 device ---------')
            # 加载数据
            data.load_eeg_ar2_one_night() if data.eeg_path is not None else None
            data.load_acc() if data.acc_path is not None else None
            logging.info('load data success.')
            # 保存mat
            data.save_mat()
            logging.info('save data to mat success.')
            # 重采样
            data.eeg_acc_reshape()
            logging.info('down sample success.')
            # data preview
            plot_preview_mr2(data.eeg0, data.eeg1, data.acc, data.start_time, data.sf_eeg, data.eeg_path)
            logging.info('plot data success.')
            data.clear_mr_data()
            # save pdf
            generate_data_preview(data)
            logging.info('save data preview success.')

        else:
            logging.info('Unknown Device Type:{}'.format(data.device))

    except Exception as e:
        logging.error(f"{e}")
