from typing import Collection
import numpy as np
import pandas as pd


def say_hi():
    print("Hello there!")
    return

def use_np():
    
    return np.linspace(0, 1)

def use_pandas():
    data = [
        [1, 2, "0"],
        [2, 4, "0"],
        [3, 3, "1"],
        [4, 1, "1"]
    ]

    return pd.DataFrame(data, columns=["x", "y", "label"])
