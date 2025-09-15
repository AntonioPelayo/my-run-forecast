import pandas as pd
import fitparse

import config
from utils.transformations import create_elapsed_time, create_gradient

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


def parse_fit_file(fit_path, metric=True):
    """Parse a .fit file into a DataFrame with a known structure."""
    fit = fitparse.FitFile(fit_path)
    rows = []

    for record in fit.get_messages('record'):
        record = {d.name: d.value for d in record}
        rows.append(record)

    if not rows:
        return pd.DataFrame(columns=config.EXPECTED_FIT_COLUMNS)

    df = pd.DataFrame(rows)

    # Remove unknown columns
    df = df[[col for col in df.columns if 'unknown' not in col]]

    # Standardize units and columns
    if 'enhanced_altitude' in df.columns:
        df['altitude_m'] = pd.to_numeric(df['enhanced_altitude'], errors='coerce')
    elif 'altitude' in df.columns:
        df['altitude_m'] = pd.to_numeric(df['altitude'], errors='coerce')

    if 'enhanced_speed' in df.columns:
        df['speed_mps'] = pd.to_numeric(df['enhanced_speed'], errors='coerce')
    elif 'speed' in df.columns:
        df['speed_mps'] = pd.to_numeric(df['speed'], errors='coerce')

    if 'distance' in df.columns:
        df['distance_m'] = pd.to_numeric(df['distance'], errors='coerce')

    if 'fractional_cadence' in df.columns:
        df['cadence'] = pd.to_numeric(df['cadence'], errors='coerce')
        df['cadence'] += pd.to_numeric(df['fractional_cadence'], errors='coerce')

    # New data fields
    df = create_elapsed_time(df)
    df = create_gradient(df)

    # Drop original columns after conversion
    df.drop(columns=[
        col for col in [
            'altitude', 'enhanced_altitude', 'fractional_cadence',
            'enhanced_speed', 'speed'
        ]
        if col in df.columns],
        inplace=True
    )

    # vertical change (signed), positive gains, and cumulative gain
    df['vert_change_m'] = df['altitude_m'].diff().fillna(0)
    df['vert_gain_m'] = df['vert_change_m'].clip(lower=0)
    df['cum_vert_gain_m'] = df['vert_gain_m'].cumsum()

    # Convert units
    if not metric:
        if 'altitude_m' in df.columns:
            df['altitude_ft'] = df['altitude_m'] * 3.28084
        if 'distance_m' in df.columns:
            df['distance_mi'] = df['distance_m'] * 0.000621371
        if 'vert_change_m' in df.columns:
            df['vert_change_ft'] = df['vert_change_m'] * 3.28084
        if 'vert_gain_m' in df.columns:
            df['vert_gain_ft'] = df['vert_gain_m'] * 3.28084
        if 'cum_vert_gain_m' in df.columns:
            df['cum_vert_gain_ft'] = df['cum_vert_gain_m'] * 3.28084
        if 'speed_mps' in df.columns:
            df['speed_mph'] = df['speed_mps'] * 2.23694
        if 'step_length' in df.columns:
            df['step_length_ft'] = df['step_length'] * 0.00328084
        if 'temperature' in df.columns:
            df['temperature_f'] = (df['temperature'] * 9/5) + 32

        df.drop(columns=[
            col for col in [
                'altitude_m', 'delta_altitude_m',
                'distance_m', 'delta_distance_m',
                'speed_mps', 'step_length', 'temperature',
                'vert_change_m', 'vert_gain_m', 'cum_vert_gain_m'
            ]
            if col in df.columns],
            inplace=True
        )

    df.reset_index(drop=True, inplace=True)
    return df
