# my-run-forecast
Analysis of relationships between pace, elevation, and heart rate, with models for effort categorization and route completion time prediction.

## Structure
- `notebooks/`: exploratory and modeling notebooks.
  - `01-data-ingestion.ipynb`: ingest `.fit` files, clean, and save as parquet.
- `utils/`: shared helpers.
  - `utils/fit.py`: FIT parsing and conversion.
- `data/`: raw files (`.fit`)
