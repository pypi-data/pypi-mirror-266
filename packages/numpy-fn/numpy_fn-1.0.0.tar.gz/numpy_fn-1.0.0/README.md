![CI](https://github.com/ywatanabe1989/torch_fn/actions/workflows/pip_install.yml/badge.svg)
![CI](https://github.com/ywatanabe1989/torch_fn/actions/workflows/run_example.yml/badge.svg)

## Installation
``` bash
$ pip install numpy_fn
```

## Usage

``` python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-07 21:56:35 (ywatanabe)"

from numpy_fn import numpy_fn

import numpy as np
import pandas as pd
import scipy
import torch


@numpy_fn
def numpy_softmax(*args, **kwargs):
    return scipy.special.softmax(*args, **kwargs)


def custom_print(x):
    print(type(x), x)


# Test the decorator with different input types
x = [1, 2, 3]
x_list = x
x_array = np.array(x)
x_df = pd.DataFrame({"col1": x})
x_tensor = torch.tensor(x).float()
if torch.cuda.is_available():
    x_tensor_cuda = torch.tensor(x).float().cuda()

custom_print(numpy_softmax(x_list, axis=-1))
# <class 'numpy.ndarray'> [0.09003057 0.24472847 0.66524096]

custom_print(numpy_softmax(x_array, axis=-1))
# <class 'numpy.ndarray'> [0.09003057 0.24472847 0.66524096]

custom_print(numpy_softmax(x_df, axis=-1))
# <class 'numpy.ndarray'> [0.09003057 0.24472847 0.66524096]

custom_print(numpy_softmax(x_tensor, axis=-1))
# /home/ywatanabe/proj/numpy_fn/src/numpy_fn/_numpy_fn.py:57: UserWarning: Converted from  <class 'numpy.ndarray'> to <class 'torch.Tensor'> (cpu)
#   warnings.warn(
# <class 'torch.Tensor'> tensor([0.0900, 0.2447, 0.6652])

if torch.cuda.is_available():
    custom_print(numpy_softmax(x_tensor_cuda, axis=-1))
# /home/ywatanabe/proj/numpy_fn/src/numpy_fn/_numpy_fn.py:57: UserWarning: Converted from  <class 'numpy.ndarray'> to <class 'torch.Tensor'> (cuda:0)
#   warnings.warn(
# <class 'torch.Tensor'> tensor([0.0900, 0.2447, 0.6652], device='cuda:0')
```
