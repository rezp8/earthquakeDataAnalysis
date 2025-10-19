import pandas as pd


def count_missing_values(df):
    return df.isna().sum().to_dict()
