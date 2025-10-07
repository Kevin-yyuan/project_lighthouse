#!/bin/bash

# Run data pipeline if database does not exist
if [ ! -f lighthouse.db ]; then
  echo "Database not found. Running data pipeline..."
  python 1_generate_data.py
  python 2_build_database.py
  python 3_enhanced_prediction_model.py
fi

# Start the Gunicorn server
gunicorn --bind 0.0.0.0:5001 4_app:app
