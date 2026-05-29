import pandas as pd
import numpy as np
from datetime import datetime

from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer

from credit_risk.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()

# Defining some constants
W = 24
RAW_DATA_PATH = RAW_DATA_DIR / "accepted_2007_to_2018q4.csv"
STATUS_TO_LABEL = {
    'Fully Paid':                                           0,                                           
    'Current':                                              0,
    'Charged Off':                                          1,
    'Late (31-120 days)':                                   1,
    'In Grace Period':                                      None,
    'Late (16-30 days)':                                    None,
    'Does not meet the credit policy. Status:Fully Paid':   0,
    'Does not meet the credit policy. Status:Charged Off':  1,
    'Default':                                              1,
}
SPLIT_YEARS = {
    'train':    (2007, 2014),
    'val':      (2015, 2015),
    'test':     (2016, 2016),
}

# functions
def load_data(path: Path) -> pd.DataFrame:
    logger.info("Loading the raw...")
    raw_data = pd.read_csv(
        filepath_or_buffer=path,
        encoding='latin-1',
        sep=",",
        thousands=',',
        na_values=['NA', 'N/A', 'null', 'NULL', '', ' ', 'None'],
        low_memory=False,
        nrows=1000
    )
    
    # doing a bit cleaning and dtype correction
    parse_dates = ['issue_d']
    
    # correcting the dates format
    raw_data[parse_dates] = raw_data[parse_dates].apply(lambda x: pd.to_datetime(x, format="%b-%Y", errors='coerce'))
    raw_data.dropna(subset=parse_dates, inplace=True)
    
    # check if everything worked correctly
    for col in parse_dates:
        assert pd.api.types.is_datetime64_any_dtype(raw_data[col]), (
            f"{col} is not a datetime column!"
        )
        
    logger.info(f"Loaded successfully! {raw_data.shape[0]} rows and {raw_data.shape[1]} columns!")
    return raw_data

def compute_snapshot_date(data: pd.DataFrame) -> pd.Timestamp:
    
    logger.info("Calculating the snapshot date...")
    
    ss_date = data['issue_d'].max()
    
    logger.info(f'Calculated snapshot date: {ss_date}')
    
    assert pd.notna(ss_date), (
        "snapshot date is NaT — check issue_d column!"
    )
    return ss_date 

def apply_observation_window(
    data: pd.DataFrame,
    W: int,
    ss_date: pd.Timestamp
) -> pd.DataFrame:
    
    logger.info(f"Filtering out the loans with are not older than {W} months")
    logger.info(f"Input: {len(data)} rows and {data.shape[1]} columns")
    loan_age_months = ss_date.to_period('M').ordinal - data['issue_d'].dt.to_period('M').astype(int)
    filtered_idx = loan_age_months[loan_age_months >= W].index
    
    logger.info(f"Output: After filtering {len(data.loc[filtered_idx])} and {data.shape[1]} columns survived!")
    
    return data.loc[filtered_idx]

def build_target(data: pd.DataFrame) -> pd.DataFrame:
    
    logger.info("Building the target...")
    logger.info(f"Input: Got {len(data)} rows and {data.shape[1]} columns")
    
    drop_vals = [key for key, value in STATUS_TO_LABEL.items() if value is None]
    ones_vals = [key for key, value in STATUS_TO_LABEL.items() if value is 1]
    
    drop_mask = data['loan_status'].isin(drop_vals)
    data = data[~drop_mask]
    
    ones_mask = data['loan_status'].isin(ones_vals)
    target = np.where(ones_mask, 1, 0)
    
    data['target'] = target
    
    assert 'target' in data.columns, "target column not added"
    assert set(data['target'].unique()) == {0,1}, "target is not set properly, has more values apart from {0,1}"
    
    logger.info(f"Output: survived {len(data)} rows and {data.shape[1]} columns")
    return data

def make_splits(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    
    logger.info(f"Input Got {data.shape[0]} rows and {data.shape[1]} columns")
    
    training_mask = (data['issue_d'] >= datetime(year=SPLIT_YEARS['train'][0], month=1, day=1)) & (data['issue_d'] <= datetime(year=SPLIT_YEARS['train'][1], month=12, day=31))
    val_mask = (data['issue_d'] >= datetime(year=SPLIT_YEARS['val'][0], month=1, day=1)) & (data['issue_d'] <= datetime(year=SPLIT_YEARS['val'][1], month=12, day=31))
    test_mask = (data['issue_d'] >= datetime(year=SPLIT_YEARS['test'][0], month=1, day=1)) & (data['issue_d'] <= datetime(year=SPLIT_YEARS['test'][1], month=12, day=31))
    
    training_set = data[training_mask]
    val_set = data[val_mask]
    test_set = data[test_mask]
    
    logger.info(f"Splited the data: Training data shape: {training_set.shape} with default rate: {(training_set['target'].sum()/len(training_set))*100}%, Val data shape: {val_set.shape} with default rate: {(training_set['target'].sum()/len(training_set))*100}%, Testing data shape: {test_set.shape} with default rate: {(training_set['target'].sum()/len(training_set))*100}%")

    return (training_set, val_set, test_set)

def build_dataset(
    raw_path: Path = RAW_DATA_PATH,
    processed_dir: Path = PROCESSED_DATA_DIR,
    W: int = W,
    force_rebuild: bool = False
) -> None:
    logger.info("Checking the permission to Build the complete dataset...")
    
    is_empty = not any(processed_dir.iterdir())
    if not is_empty and not force_rebuild:
        logger.info(f"Skipping the build, data already exists inside {processed_dir}")
    else:
        df = load_data(path=raw_path)
        ss_date = compute_snapshot_date(data=df)
        df = apply_observation_window(data=df, ss_date=ss_date, W=W)
        df = build_target(data=df)
        splits = make_splits(data=df)
        
        splits[0].to_parquet(path=processed_dir / "training_set.parquet")
        splits[1].to_parquet(path=processed_dir / "val_set.parquet")
        splits[2].to_parquet(path=processed_dir / "test_set.parquet")
        


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_PATH,
    output_path: Path = PROCESSED_DATA_DIR,
    # ----------------------------------------------
):
    pass


if __name__ == "__main__":
    app()
