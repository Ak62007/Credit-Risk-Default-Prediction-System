from pathlib import Path

from loguru import logger
import pandas as pd
import numpy as np
import joblib
import typer
import json
import shap

from credit_risk.config import MODELS_DIR, PROCESSED_DATA_DIR
from credit_risk.features import add_credit_yrs, add_fico_mid, drop_columns, CATEGORICAL_COLS

app = typer.Typer()

model_path = MODELS_DIR / "tuned_xgb"

logger.info("Loading the preprocessor and tuned xgb model...")
model = joblib.load(model_path / 'model.pkl')
logger.info("Both loaded successfully!")

logger.info("Building the col to onehot cols list map...")
features_name = model[0].get_feature_names_out()
features_name = np.char.replace(features_name.astype(str), "<", "lt")
CAT_TO_ONEHOT = {}
for col in CATEGORICAL_COLS:
    CAT_TO_ONEHOT[col] = [onehot for onehot in features_name if onehot.startswith(f"cat__{col}_")]
    
logger.info(f"CAT_TO_ONEHOT map built successfully!")

logger.info("Creating the SHAP Explainer...")
explainer = shap.TreeExplainer(model=model[1])
logger.info("SHAP explainer created successfully!")

logger.info("Loading the threshold to make the prediction...")
with open(model_path / 'metrics.json', 'r') as f:
    metrics = json.load(f)
    
threshold = metrics['threshold']
    
logger.info("Loaded successfully!")


def predict_one(raw_input: dict) -> tuple[int, float, dict]:
    """columns required in the raw_input for correct functioning of the fuction are the following:
    Bucket 1 — raw fields the caller supplies directly, used as-is by the model.
    Bucket 2 — raw fields the caller supplies, but only so you can derive something from them; they never reach the model directly. earliest_cr_line and fico_range_low/fico_range_high. 
    Args:
        raw_input (dict): The raw input on which the best model will do the prediction
    """
    logger.info("Adding the transformed features...")
    df = pd.DataFrame.from_records([raw_input])
    logger.info("Adding the issue date as now...")
    df['issue_d'] = pd.Timestamp.now()
    df = add_credit_yrs(df)
    df = add_fico_mid(df)
    df = drop_columns(df)
    logger.info("Successfully added!")
    
    
    logger.info("Starting tranformation and inference...")
    t_df = model[0].transform(df)
    prob = model[1].predict_proba(t_df)[:, 1]
    logger.info(f"Predicted prob: {prob[0]}")
    prediction = 1 if float(prob[0]) >= threshold else 0
    logger.info("Inference Done!")
    
    logger.info("Starting the Explaination step...")
    t_df = pd.DataFrame(t_df, columns=features_name)
    explaination = explainer(t_df)
    shap_df = pd.DataFrame({
        "feature": explaination.feature_names,
        'shap_value': explaination.values[0]
    })
    
    for cat_col, onehot in CAT_TO_ONEHOT.items():
        agg = shap_df[shap_df['feature'].isin(onehot)]['shap_value'].sum()
        new_row = pd.DataFrame([[f"cat__{cat_col}", agg]], columns=shap_df.columns)
        shap_df = pd.concat([shap_df, new_row], ignore_index=True)
        shap_df = shap_df[~shap_df['feature'].isin(onehot)]
        
    shap_df = shap_df.sort_values('shap_value', key=abs, ascending=False)
        
    reason_codes = {row.feature : row.shap_value for row in shap_df.head().itertuples(index=False)}
    
    return (prediction, float(prob[0]), reason_codes)

@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    features_path: Path = PROCESSED_DATA_DIR / "test_features.csv",
    model_path: Path = MODELS_DIR / "tuned_xgb" / "model.pkl",
    predictions_path: Path = PROCESSED_DATA_DIR / "predictions" / "test_predictions.csv",
    # -----------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Performing inference for model...")
    
    logger.success("Inference complete.")
    # -----------------------------------------


if __name__ == "__main__":
    app()
