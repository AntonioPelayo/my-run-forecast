from pathlib import Path
from typing import Union

import pandas as pd
from fitparse import FitFile

from config import (
    EXPECTED_FIT_COLUMNS,
    UNKNOWN_COLUMN_MAP,
    M_TO_FT_MULTIPLIER,
    M_TO_MI_MULTIPLIER,
    MPS_TO_MPH_MULTIPLIER,
    MM_TO_FT_MULTIPLIER,
)
from utils.features import (
    elapsed_seconds, compute_gradient, percent_grade, grade_degrees
)


def list_fit_files(directory: Union[str, Path]) -> list[Path]:
    """Return a list of .fit files in the given directory."""
    directory = Path(directory)
    return list(directory.glob('*.fit'))


def get_sport(fit: FitFile) -> Union[str, str]:
    """Return the sport string from a FIT file, if present. Lowercased when returned."""
    sport = ''
    sub_sport = ''

    for msg in fit.get_messages('session'):
        fields = {f.name: f.value for f in msg}
        if fields.get('sport') is not None and sport == '':
            sport = str(fields['sport']).lower()
        if fields.get('sub_sport') is not None and sub_sport == '':
            sub_sport = str(fields['sub_sport']).lower()
        if sport != '' and sub_sport != '':
            break

    if sport == '' or sub_sport == '':
        for msg in fit.get_messages('sport'):
            fields = {f.name: f.value for f in msg}
            if sport == '' and fields.get('sport') is not None:
                sport = str(fields['sport']).lower()
            if sub_sport == '' and fields.get('sub_sport') is not None:
                sub_sport = str(fields['sub_sport']).lower()
            if sport != '' and sub_sport != '':
                break

    return sport, sub_sport


def fit_to_df(fit: FitFile) -> pd.DataFrame:
    """Read a .fit file and return a pandas DataFrame."""
    rows = []
    for record in fit.get_messages('record'):
        data = {d.name: d.value for d in record}
        rows.append(data)

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=EXPECTED_FIT_COLUMNS)

    df.rename(columns=UNKNOWN_COLUMN_MAP, inplace=True)
    df['sport'], df['sub_sport'] = get_sport(fit)
    return df


def fit_to_parquet(fit: FitFile, parquet_path: str) -> None:
    """Convert a .fit file to a Parquet file."""
    df = fit_to_df(fit)
    df.to_parquet(parquet_path, index=False)


def standardize_fit_df(df: pd.DataFrame) -> pd.DataFrame:
    if 'fractional_cadence' in df.columns:
        df['complete_cadence'] = df['cadence'] + df['fractional_cadence']

    df['elapsed_seconds'] = elapsed_seconds(df['timestamp'])

    if df['sub_sport'].iloc[0] == 'treadmill':
        df.reset_index(drop=True, inplace=True)
        return df

    df['altitude_change'] = df['enhanced_altitude'].diff().fillna(0)
    df['altitude_gain'] = df['altitude_change'].clip(lower=0)
    df['cum_altitude_gain'] = df['altitude_gain'].cumsum()

    df['gradient'] = compute_gradient(df['enhanced_altitude'], df['distance'])
    df['percent_grade'] = percent_grade(df['gradient'])
    df['grade_degrees'] = grade_degrees(df['gradient'])

    df.reset_index(drop=True, inplace=True)
    return df
