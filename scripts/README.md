# Scripts

## activity_summary.py
- **Purpose**: Print summary statistics for a single activity file.
- **Defaults**: None.
- **Run command**:
```bash
python3 -m scripts.activity_summary PATH_TO_ACTIVITY_FILE
```

### Arguments
- `activityFile` (positional): Path to a single activity file in parquet format


## fit_ingestion.py
Modern ingestion entry point for FIT files that powers the parquet activity archive.

- **Purpose**: Parse Garmin `.fit` files, keep only running activities, and materialize them as parquet datasets for downstream analytics.
- **Defaults**: When no paths are supplied, the script reads from `config.GARMIN_FIT_ACTIVITIES_PATH` and writes into `config.PARQUET_RUN_ACTIVITIES_PATH`.
- **Run command**:
```bash
python3 -m scripts.fit_ingestion [--source PATH] [--destination PATH] [--mode {replace,incremental}]
```

### Arguments
- `--source / -s` (optional): Directory containing the raw `.fit` files. Defaults to `config.GARMIN_FIT_ACTIVITIES_PATH`.
- `--destination / -d` (optional): Directory that will receive the parquet outputs. Defaults to `config.PARQUET_RUN_ACTIVITIES_PATH`.
- `--mode` (optional, default `incremental`):
  - `incremental`: Skip any file that already exists as a parquet in the destination (matched on filename stem).
  - `replace`: Remove the destination directory before ingestion, ensuring a clean rebuild.

### Operational Notes
- Only activities identified as `running` (using `utils.fit.get_sport_from_fit`) are converted.


## gpx_time_predictor.py
