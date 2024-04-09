import numpy as np


def load_sti(sti_path):
    index_list = []
    with open(sti_path, 'r') as f:
        for line in f:
            if line.startswith("point count: "):
                index = line.split("\t")[0][13:]
                index_list.append(int(index) // 5)
    index_list = np.array(index_list, dtype=np.int32) if len(index_list) >= 2 else None
    return index_list


if __name__ == '__main__':
    sti_path_ = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\sti.log'
    sti_data = load_sti(sti_path_)
