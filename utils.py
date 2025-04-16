import pandas as pd
import os

def load_data(file_path, columns):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=columns)

def save_data(file_path, df):
    df.to_csv(file_path, index=False)
