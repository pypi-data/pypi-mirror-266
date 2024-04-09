
from qleegss.plot.plot_sw import plot_sw
from qleegss.plot.plot_stage import plot_stage
from qleegss.other.metric import sleep_metrics
from qleegss.pdf.sleep_report import generate_sleep_report
import logging
from qleegss.plot.plot_data_preview import plot_preview_mr4
from qleegss.pdf.data_preview import generate_data_preview
from qleegss.plot.plot_data_preview import plot_preview_mr2
import tracemalloc
from qleegss.handler import DataHandler


if __name__ == '__main__':
    tracemalloc.start()  # 开始跟踪内存分配
    logging.basicConfig(filename='example.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    eeg_path = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\eeg.eeg'
    acc_path = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\acc.acc'
    sti_path = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\sti.log'
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    try:
        data = DataHandler(eeg_path, acc_path, sti_path)
        data.load_device_type()
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
        if data.device == 101:
            logging.info('--------- X8 device ---------')
            data.load_eeg_x8_one_night() if data.eeg_path is not None else None
            data.load_acc() if data.acc_path is not None else None
            data.load_sti() if data.sti_path is not None else None
            print('load data success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
            # 保存mat
            data.save_mat()
            logging.info('save data to mat success.')
            print('load data success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
            # 重采样
            data.eeg_acc_reshape()
            logging.info('down sample success.')
            print('load data success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
            # 慢波图绘制
            plot_sw(data.eeg, data.start_time, data.sf_eeg, data.eeg_path, data.sti) if data.sti is not None else None
            print('slow wave success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
            # 清除sti
            data.clear_sti()
            # 生成分期
            data.sleep_stage()
            print('sleep stage success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
            # 绘制分期
            plot_stage(data.eeg, data.start_time, data.sf_eeg, data.eeg_path, data.acc, data.stage_result)
            print('plot stage success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
            # 清数据
            data.clear_eeg()
            data.clear_acc()
            # 计算睡眠指标&保存成excel
            sleep_metrics(data.eeg_path, data.stage_result)
            print('save xlsx success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
            # pdf
            generate_sleep_report(data)
            print('save report success.')
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
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
            logging.info('Unknown Device Type')

    except Exception as e:
        logging.error(f"{e}")
