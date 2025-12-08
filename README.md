# my-run-forecast
Exploratory analysis of relationships between pace, elevation, and heart rate, with models for effort categorization and route completion time prediction. `.fit` activity data collected using a Garmin Fenix 8 and `.gpx` routes built and exported using Strava.

## Structure
- `data/`: Activity and route files.
- `models/`: Time prediction and effort categorization models.
- `notebooks/`: Exploratory and modeling notebooks.
- `scripts/`: Executable scripts.
- `utils/`: Shared helpers.

## Data
Data from `.fit` files are recorded in metric units. Imperial conversions are applied only after all data manipulations and are used exclusively for final display and visualization.

## Usage
### Setup
Create and activate a virtual environment, then install dependencies.

### Data Ingestion
Connect watch to computer and using an app such as "Android File Transfer" copy the `.fit` files from `GARMIN/ACTIVITY` to `data/garmin_fit_activities/`.

Then run the ingestion script to filter for running activities and convert `.fit` files to parquet into `data/parquet_run_activities/`.
```bash
./venv/bin/python -m scripts.fit_ingestion
```
