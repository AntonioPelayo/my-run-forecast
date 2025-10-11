import argparse
from pathlib import Path

# from utils import activity as au

from utils.fit import is_run_activity, fit_to_df, parse_fit_file
from config import GARMIN_FIT_ACTIVITIES_PATH, PARQUET_RUN_ACTIVITIES_PATH

def main():
    """Convert all .fit files in GARMIN_FIT_ACTIVITIES_PATH to Parquet files in PARQUET_RUN_ACTIVITIES_PATH."""
    print(f"{len(list(GARMIN_FIT_ACTIVITIES_PATH.glob('*.fit')))} .fit files found in {GARMIN_FIT_ACTIVITIES_PATH}")
    run_activies_count = 0

    for fit_file in GARMIN_FIT_ACTIVITIES_PATH.glob("*.fit"):
        df = fit_to_df(str(fit_file))

        if is_run_activity(df):
            df = parse_fit_file(str(fit_file))
            df.to_parquet(PARQUET_RUN_ACTIVITIES_PATH / f"{fit_file.stem}.parquet", index=False)
            run_activies_count += 1

    print(f"{run_activies_count} run activities converted to Parquet in {PARQUET_RUN_ACTIVITIES_PATH}")

if __name__ == "__main__":
    main()
