import pandas as pd
import fitparse

def fit_to_df(file_path):
    """Read a .fit file and return a pandas DataFrame."""
    fitfile = fitparse.FitFile(file_path)
    records = []
    for record in fitfile.get_messages('record'):
        record_data = {}
        for data in record:
            record_data[data.name] = data.value
        records.append(record_data)
    df = pd.DataFrame(records)
    return df

def fit_to_parquet(fit_path, parquet_path):
    """Convert a .fit file to a Parquet file."""
    df = fit_to_df(fit_path)
    df.to_parquet(parquet_path, index=False)
