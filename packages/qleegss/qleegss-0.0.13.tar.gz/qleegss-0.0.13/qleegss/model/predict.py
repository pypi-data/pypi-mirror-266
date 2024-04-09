import numpy as np
import torch
import os
from qleegss.model.sleepyco_net import MainModel
from tqdm import tqdm
import tracemalloc


def predict_one_trail(eeg):
    net = create_model()
    res = []
    net.eval()
    eeg = torch.from_numpy(eeg.reshape(-1, 100*30)).float()
    with torch.no_grad():
        for inputs in tqdm(eeg):
            inputs = inputs.reshape(1, 1, -1)
            outputs = net(inputs)
            outputs_sum = torch.zeros_like(outputs[0])

            for j in range(len(outputs)):
                outputs_sum += outputs[j]
            predicted = torch.argmax(outputs_sum)
            res.append(predicted.item())
        map_dict = {
            3: 0,
            2: 1,
            1: 2,
            4: 3,
            0: 4,
            5: 5
        }
        #
        res = [map_dict.get(x, x) for x in res]
    return np.asarray(res)


def predict_one_epoch(eeg):
    net = create_model()
    net.eval()
    eeg = torch.from_numpy(eeg).reshape(1, 1, -1).float()
    with torch.no_grad():
        outputs = net(eeg)
        outputs_sum = torch.zeros_like(outputs[0])
        for j in range(len(outputs)):
            outputs_sum += outputs[j]
        predicted = torch.argmax(outputs_sum)
        map_dict = {
            3: 0,
            2: 1,
            1: 2,
            4: 3,
            0: 4,
            5: 5
        }
    return map_dict.get(int(predicted.item()))


def create_model():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    net = MainModel()
    net.eval()
    state_dict = torch.load(script_dir + '/ckpt_fold-01.pth', map_location=torch.device('cpu'))
    new_state_dict = {}
    for k, v in state_dict.items():
        name = k.replace('module.', '')
        new_state_dict[name] = v
    net.load_state_dict(new_state_dict)
    return net


if __name__ == '__main__':
    tracemalloc.start()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    x_ = torch.rand((1, 1, 30 * 100 * 10))
    net_ = create_model()
    net_.eval()
    with torch.no_grad():
        res_ = net_(x_)
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
