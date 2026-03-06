#!/bin/bash

source ./venv/bin/activate

# Transform new data
echo "Ingesting new data..."
python -m scripts.fit_ingestion -s ../data/GARMIN/Activity

echo "Exporting run activity summaries to CSV..."
python -m scripts.export_run_summaries

echo "Training linear regression model..."
python -m gpx_time_prediction_models.training.train_linear

echo "Data ingestion and model training complete."
