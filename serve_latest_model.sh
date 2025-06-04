#!/bin/bash

# Check if virtualenv is installed, install if missing
if ! command -v virtualenv &> /dev/null; then
    echo "virtualenv not found. Installing virtualenv..."
    pip install virtualenv
fi

# Activate virtual environment if needed
source venv/bin/activate

# Get the latest run_id for the experiment
EXPERIMENT_NAME="CustomerChurnPipeline"
RUN_ID=$(python -c "
import mlflow
from mlflow.tracking import MlflowClient
exp = mlflow.get_experiment_by_name('$EXPERIMENT_NAME')
if exp is None:
    exit(1)
runs = mlflow.search_runs([exp.experiment_id], order_by=['start_time DESC'])
if runs.empty:
    exit(1)
client = MlflowClient()
for _, run in runs.iterrows():
    run_id = run['run_id']
    artifacts = client.list_artifacts(run_id)
    if any(artifact.path == 'best_model' for artifact in artifacts):
        print(run_id)
        exit(0)
exit(1)
")

if [ -z "$RUN_ID" ]; then
    echo "No run found for experiment $EXPERIMENT_NAME with best_model artifact"
    exit 1
fi

echo "Serving model from run: $RUN_ID"
mlflow models serve -m runs:/$RUN_ID/best_model --port 5010 
# --host 0.0.0.0 