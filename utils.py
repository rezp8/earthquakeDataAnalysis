import numpy as np
import pandas as pd
import requests
from io import StringIO

def api_code():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "csv",
        "starttime": "2025-9-15",
        "endtime": "2025-10-20", 
        "minlatitude": 24,
        "maxlatitude": 46,
        "minlongitude": 123,
        "maxlongitude": 146,
        "minmagnitude": 0
    }
    response = requests.get(url, params=params)
    df_direct = pd.read_csv(StringIO(response.text))
    direct_count = len(df_direct) - 1
    return direct_count

def clean_data(df):
    return df.dropna()

def compute_statistics(df, column):
    return {
        "mean": df[column].mean(),
        "std": df[column].std(),
        "min": df[column].min(),
        "max": df[column].max()
    }

def validate_data_integrity(df):
    assert "latitude" in df.columns
    assert "longitude" in df.columns
    assert len(df) > 0
    return True

def calculate_distance_to_tokyo(df):
    tokyo_lat, tokyo_lon = 35.6895, 139.6917
    lat1 = np.radians(df["latitude"])
    lon1 = np.radians(df["longitude"])
    lat2 = np.radians(tokyo_lat)
    lon2 = np.radians(tokyo_lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    df["dist_to_tokyo_km"] = round(6371 * c,2)
    return df

def compute_numpy_statistics(df):
    magnitudes = df["mag"].to_numpy()
    distances = df["dist_to_tokyo_km"].to_numpy()

    return {
        "mean_mag": np.mean(magnitudes),
        "std_mag": np.std(magnitudes),
        "mean_distance": np.mean(distances)
    }

def count_missing_values(df):
    return df.isna().sum().to_dict()
