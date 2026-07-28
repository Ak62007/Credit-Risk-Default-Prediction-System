import mlflow
import mlflow.pyfunc
from mlflow import MlflowClient
import joblib
from dotenv import load_dotenv
load_dotenv()


experiment_name = "production_model_storage"
experiment = mlflow.get_experiment_by_name(experiment_name)
if experiment is None:
    mlflow.create_experiment(
        name=experiment_name,
        artifact_location="s3://credit-risk-model-artifacts-aditya62007/mlflow-artifacts",
    )
mlflow.set_experiment(experiment_name)


class CreditRiskModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.preprocessor, self.classifier = joblib.load(context.artifacts["model"])

    def predict(self, context, model_input):
        transformed = self.preprocessor.transform(model_input)
        return self.classifier.predict_proba(transformed)[:, 1]


with mlflow.start_run() as run:
    logged_model = mlflow.pyfunc.log_model(
        name="model",
        python_model=CreditRiskModel(),
        artifacts={"model": "models/tuned_xgb/model.pkl"},
    )
    mlflow.log_artifact("models/tuned_xgb/metrics.json")

mv = mlflow.register_model(f"models:/{logged_model.model_id}", "credit_risk_tuned_xgb")

client = MlflowClient()
client.set_registered_model_alias(
    name="credit_risk_tuned_xgb",
    alias="production",
    version=mv.version,
)