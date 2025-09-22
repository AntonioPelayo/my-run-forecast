# my-run-forecast
Exploratory analysis of relationships between pace, elevation, and heart rate, with models for effort categorization and route completion time prediction. `.fit` activity data collected using a Garmin Fenix 8 and `.gpx` routes built and exported from Strava.

## Structure
- `notebooks/`: Exploratory and modeling notebooks.
  - `01-data-ingestion.ipynb`: Ingest `.fit` files, clean, and save as parquet.
  - `02-feature-engineering.ipynb`: Uses `utils/` to build new features and convert from metric to imperial.
- `scripts/`: Executable scripts.
  - `activity_summary.py`: Print summary statistics for a single activity file.
  - `gpx_time_predictor.py`: Predict time to complete a route given distance and elevation gain.
- `utils/`: Shared helpers.
  - `activity.py`: Activity loading and summary functions.
  - `features.py`: Feature engineering functions.
  - `fit.py`: FIT parsing and conversion.
  - `gpx.py`: GPX parsing and route summary.
  - `time.py`: Time functions.
- `data/`: raw files (`.fit`)


## Usage
`activity_summary.py`
```bash
./venv/bin/python -m scripts.activity_summary ./data/activity.parquet
```