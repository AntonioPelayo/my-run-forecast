# my-run-forecast
Exploratory analysis of relationships between pace, elevation, and heart rate, with models for effort categorization and route completion time prediction. `.fit` activity data collected using a Garmin Fenix 8 and `.gpx` routes built and exported from Strava.

## Structure
- `notebooks/`: Exploratory and modeling notebooks.
  - `01-data-ingestion.ipynb`: Ingest `.fit` files, clean, and save as parquet.
  - `02-feature-engineering.ipynb`: Uses `utils/` to build new features and convert from metric to imperial.
- `utils/`: Shared helpers.
  - `fit.py`: FIT parsing and conversion.
  - `transformations.py`: New feature creation and unit conversions.
- `data/`: raw files (`.fit`)
