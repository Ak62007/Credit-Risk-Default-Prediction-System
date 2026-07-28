from dotenv import load_dotenv
load_dotenv()

import os
import shutil
import mlflow
from mlflow import MlflowClient

client = MlflowClient()

mv = client.get_model_version_by_alias("credit_risk_tuned_xgb", "production")

os.makedirs("models/tuned_xgb", exist_ok=True)

local_model_dir = mlflow.artifacts.download_artifacts(artifact_uri="models:/credit_risk_tuned_xgb@production")
shutil.copy(os.path.join(local_model_dir, "artifacts", "model.pkl"), "models/tuned_xgb/model.pkl")

metrics_path = mlflow.artifacts.download_artifacts(run_id=mv.run_id, artifact_path="metrics.json")
shutil.copy(metrics_path, "models/tuned_xgb/metrics.json")

print("Fetched model.pkl and metrics.json into models/tuned_xgb/")