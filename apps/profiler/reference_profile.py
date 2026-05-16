import pandas as pd

def build_reference_profile(df):
    profile = {}

    for col in df.columns:
        profile[col] = {
            "dtype": str(df[col].dtype),
            "nulls": df[col].isnull().sum(),
            "unique_ratio": df[col].nunique() / len(df),
            "sample_values": df[col].dropna().unique()[:10].tolist()
        }

    return profile