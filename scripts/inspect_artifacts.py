from dotenv import load_dotenv
load_dotenv()

import mlflow


local_path = mlflow.artifacts.download_artifacts(artifact_uri="models:/credit_risk_tuned_xgb@production")
print("Downloaded to:", local_path)

import os
for root, dirs, files in os.walk(local_path):
    for f in files:
        print(os.path.join(root, f))