# my-run-forecast
Exploratory analysis of relationships between pace, elevation, and heart rate, with models for effort categorization and route completion time prediction. `.fit` activity data collected using a Garmin Fenix 8 and `.gpx` routes built and exported from Strava.

## Structure
- `data/`: Activity and route files.
- `models/`: Time prediction and effort categorization models.
- `notebooks/`: Exploratory and modeling notebooks.
  - `01-data-ingestion.ipynb`: Ingest `.fit` files, clean, and save as parquet.
  - `02-feature-engineering.ipynb`: Uses `utils/` to build new features and convert from metric to imperial.
- `scripts/`: Executable scripts.
  - `activity_summary.py`: Print summary statistics for a single activity file.
  - `fit_ingestion.py`: Ingest Garmin `.fit` files, filter for runs, and save as parquet.
  - `gpx_time_predictor.py`: Predict time to complete a route given distance and elevation gain.
- `utils/`: Shared helpers.
  - `activity.py`: Activity loading and summary functions.
  - `features.py`: Feature engineering functions.
  - `fit.py`: FIT parsing and conversion.
  - `gpx.py`: GPX parsing and route summary.
  - `time.py`: Time functions.


## Usage
### Data Ingestion
Connect watch to computer and using an app such as "Android File Transfer" copy the `.fit` files from `GARMIN/ACTIVITY` to `data/garmin_fit_activities/`.

Then run the ingestion script to filter for running activities and convert `.fit` files to parquet into `data/parquet_run_activities/`.
```bash
./venv/bin/python -m scripts.fit_ingestion
```

### Scripts
`scripts/activity_summary.py`
```bash
./venv/bin/python -m scripts.activity_summary ./data/activity.parquet
```

`scripts/gpx_time_predictor.py`
```bash
./venv/bin/python -m scripts.gpx_time_predictor ./data/activities/ ./data/routes/route.gpx
```
