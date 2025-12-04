import pandas as pd
import numpy as np


def clean_data(data: pd.DataFrame):
    np.random.seed(0)
    print(data.head())

    missing_values_count = data.isnull().sum()
    print(missing_values_count)
