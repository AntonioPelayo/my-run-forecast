# my-run-forecast
Exploratory analysis of relationships between pace, elevation, and heart rate,
with models for effort categorization and route completion time prediction.
`.fit` activity data collected using a Garmin Fenix 8 and `.gpx` routes built
and exported using Strava.

## Project structure
```
my-run-forecast/
├── bin/                        # Executable scripts
├── dash_app/
│   ├── assets/                 # CSS and static assets
│   │   ├── plots/              # Static plot images
│   │   └── style.css           # Web app styles
│   ├── pages/
│   │   ├── blog/                   # Blog pages
│   │   ├── blog_home.py            # Blog home page
│   │   ├── gpx_time_predictor.py   # GPX Time Predictor page
│   │   └── home.py                 # Home page
│   └── app.py
├── data/
│   ├── backups/                # Backup files
│   ├── garmin_fit_files/       # Raw .fit files extracted from Garmin
│   ├── gpx_routes/             # Example GPX routes
│   ├── parquet_run_activities/ # Transformed run activities in parquet format
│   └── run_summaries.csv       # Summariezed activity data, 1 row per activity
├── gpx_time_prediction_models/
│   ├── artifacts/              # Trained model weights
│   ├── inference/              # Inference pipelines
│   └── training/               # Model training pipelines
├── notebooks/                  # Exploratory and modeling notebooks
├── scripts/                    # Executable scripts
└── utils/                      # Shared helpers
```

## Data
Data from `.fit` files are recorded in metric units.
Imperial conversions are applied only after all data manipulations and are used
exclusively for final display and visualization.

## Usage
### Setup
Create and activate a virtual environment, then install dependencies.

### Data Loading
Connect watch to computer and using an app such as "Android File Transfer" copy
the `.fit` files from `GARMIN/Activity` to `data/garmin_fit_activities/`.

Then run the ingestion script to filter for running activities and convert
`.fit` files to parquet into `data/parquet_run_activities/`.
```bash
./venv/bin/python -m scripts.fit_ingestion
```

### Dash Web App
For dash app development and testing, run the following command to start the
app locally:
```bash
./venv/bin/python -m gunicorn dash_app.app:server --reload
```
