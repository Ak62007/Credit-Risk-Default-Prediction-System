import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer

from credit_risk.config import PROCESSED_DATA_DIR
from credit_risk.dataset import AFTER_EDA, load_splits

app = typer.Typer()

def add_credit_yrs(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a feature called credit_yrs"""
    logger.info("Adding the feature 'credit_yrs'")
    df['credit_yrs'] = (df['issue_d'] - df['earliest_cr_line']).dt.days/365.25
    logger.info("'credit_yrs added successfully!'")
    return df

def add_fico_mid(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a feature called fico_mid"""
    logger.info("Adding the feature 'fico_mid'")
    df['fico_mid'] = (df['fico_range_low'] + df['fico_range_high'])/2
    logger.info("'fico_mid' added successfully!")
    return df    


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = AFTER_EDA,
    output_path: Path = PROCESSED_DATA_DIR / "features.csv",
    # -----------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Generating features from dataset...")
    for i in tqdm(range(10), total=10):
        if i == 5:
            logger.info("Something happened for iteration 5.")
    logger.success("Features generation complete.")
    # -----------------------------------------


if __name__ == "__main__":
    app()
