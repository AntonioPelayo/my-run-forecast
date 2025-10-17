from fitparse import FitFile

from utils import fit as fit_utils
from config import GARMIN_FIT_ACTIVITIES_PATH, PARQUET_RUN_ACTIVITIES_PATH

def main():
    """Convert all .fit files in GARMIN_FIT_ACTIVITIES_PATH to Parquet files in PARQUET_RUN_ACTIVITIES_PATH."""
    activity_files = list(GARMIN_FIT_ACTIVITIES_PATH.glob("*.fit"))
    print(f"{len(activity_files)} .fit files found in {GARMIN_FIT_ACTIVITIES_PATH}")
    run_activies_count = 0

    for fit_file in activity_files:
        fit = FitFile(str(fit_file))
        sport, sub_sport = fit_utils.get_sport_from_fit(fit)

        if sport != "running" and sub_sport != "running":
            continue

        df = fit_utils.parse_fit_file(fit)
        df.to_parquet(PARQUET_RUN_ACTIVITIES_PATH / f"{fit_file.stem}.parquet", index=False)
        run_activies_count += 1

    print(f"{run_activies_count} run activities converted to Parquet in {PARQUET_RUN_ACTIVITIES_PATH}")

if __name__ == "__main__":
    main()
