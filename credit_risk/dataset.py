import json
import pytest
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
AFTER_EDA = PROCESSED_DATA_DIR / "after_eda"
LEAKAGE_COLUMNS = [
    'total_pymnt',
    'total_pymnt_inv',
    'total_rec_prncp',
    'total_rec_int',
    'total_rec_late_fee',
    'recoveries',
    'collection_recovery_fee',
    'last_pymnt_d',
    'last_pymnt_amnt',
    'next_pymnt_d',
    'out_prncp',
    'out_prncp_inv',

    'last_credit_pull_d',
    'last_fico_range_high',
    'last_fico_range_low',

    'hardship_flag',
    'hardship_type',
    'hardship_reason',
    'hardship_status',
    'hardship_start_date',
    'hardship_end_date',
    'hardship_amount',
    'hardship_length',
    'hardship_dpd',
    'hardship_loan_status',
    'payment_plan_start_date',
    'deferral_term',
    'orig_projected_additional_accrued_interest',
    'hardship_payoff_balance_amount',
    'hardship_last_payment_amount',

    'debt_settlement_flag',
    'debt_settlement_flag_date',
    'settlement_status',
    'settlement_date',
    'settlement_amount',
    'settlement_percentage',
    'settlement_term',

    'id',
    'member_id',
    'url',
    'pymnt_plan',
]
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
TRAIN_FILENAME = "training_set.parquet"
VAL_FILENAME = "val_set.parquet"
TEST_FILENAME = "test_set.parquet"
METADATA_FILENAME = "metadata.json"

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
        # nrows=1000
    )
    
    # doing a bit cleaning and dtype correction
    parse_dates = ['issue_d', 'earliest_cr_line']
    
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
    
    logger.info(f"Output: After filtering {len(data.loc[filtered_idx])} rows and {data.shape[1]} columns survived!")
    
    return data.loc[filtered_idx]

def drop_leakage_columns(data: pd.DataFrame) -> pd.DataFrame:
    logger.info("Dropping The Leakage Columns...")
    logger.info(f"Input Got the data of shape: {data.shape}")
    
    before_cols = set(data.columns)
    data = data.drop(columns=LEAKAGE_COLUMNS, errors='ignore')
    after_cols = set(data.columns)
    dropped = before_cols - after_cols
    
    logger.info(f"Dropped {len(dropped)} leakage columns: {sorted(dropped)}")
    logger.info(f"Output dataframe of shape: {data.shape}")
    
    return data
    

def build_target(data: pd.DataFrame) -> pd.DataFrame:
    
    logger.info("Building the target...")
    logger.info(f"Input: Got {len(data)} rows and {data.shape[1]} columns")
    
    data = data.copy()
    
    drop_vals = [key for key, value in STATUS_TO_LABEL.items() if value is None]
    ones_vals = [key for key, value in STATUS_TO_LABEL.items() if value == 1]
    
    drop_mask = data['loan_status'].isin(drop_vals)
    data = data[~drop_mask]
    
    ones_mask = data['loan_status'].isin(ones_vals)
    target = np.where(ones_mask, 1, 0)
    
    data['target'] = target
    logger.info("Dropping the 'loan_status' column.")
    data = data.drop(columns=['loan_status'])
    
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
    
    logger.info(f"Splited the data: Training data shape: {training_set.shape} with default rate: {(training_set['target'].sum()/len(training_set))*100:.2f}%, Val data shape: {val_set.shape} with default rate: {(val_set['target'].sum()/len(val_set))*100:.2f}%, Testing data shape: {test_set.shape} with default rate: {(test_set['target'].sum()/len(test_set))*100:.2f}%")

    return (training_set, val_set, test_set)

def build_dataset(
    raw_path: Path = RAW_DATA_PATH,
    processed_dir: Path = AFTER_EDA,
    W: int = W,
    force_rebuild: bool = False
) -> None:
    logger.info("Checking the permission to Build the complete dataset...")
    
    expected_files = [processed_dir / name for name in [TRAIN_FILENAME, VAL_FILENAME, TEST_FILENAME, METADATA_FILENAME]]
    cache_complete = all(f.exists() for f in expected_files)
    if cache_complete and not force_rebuild:
        logger.info(f"Skipping the build, data already exists inside {processed_dir}")
    else:
        logger.info("Got the permissions!, Building the dataset...")
        df = load_data(path=raw_path)
        ss_date = compute_snapshot_date(data=df)
        df = apply_observation_window(data=df, ss_date=ss_date, W=W)
        df = drop_leakage_columns(df)
        df = build_target(data=df)
        no_of_rows_before_split = len(df)
        train_df, val_df, test_df = make_splits(data=df)
        
        train_df.to_parquet(path=processed_dir / TRAIN_FILENAME)
        val_df.to_parquet(path=processed_dir / VAL_FILENAME)
        test_df.to_parquet(path=processed_dir / TEST_FILENAME)
        
        # building metadata
        metadata = {
            "W": W,
            "snapshot_date": ss_date.isoformat(),
            "dropped_leakage_columns": LEAKAGE_COLUMNS,
            "target_imputation": STATUS_TO_LABEL,
            "split_years": SPLIT_YEARS,
            "row_count_before_split": no_of_rows_before_split,
            "row_counts": {
                "train": len(train_df),
                "val": len(val_df),
                "test": len(test_df),
            },
            "default_rates": {
                "train": float(train_df['target'].mean()),
                "val": float(val_df['target'].mean()),
                "test": float(test_df['target'].mean()),
            },
            "built_at": pd.Timestamp.now().isoformat(),
        }
        
        with open(processed_dir / METADATA_FILENAME, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        assert (processed_dir / TRAIN_FILENAME).exists(), ("training_set not created successfully!, File not present")
        assert (processed_dir / VAL_FILENAME).exists(), ("val_set not created successfully!, File not present")
        assert (processed_dir / TEST_FILENAME).exists(), ("test_set not created successfully!, File not present")
        assert (processed_dir / METADATA_FILENAME).exists(), ("metadata not created sucessfully!, File not present")
        
        logger.info("successfully created all three datasets and the metadata!")
        
def load_splits(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    files = [path / name for name in [TRAIN_FILENAME, VAL_FILENAME, TEST_FILENAME, METADATA_FILENAME]]
    files_exits = any(f.exists() for f in files)
    logger.info("Checking if the files exists...")    
    if files_exits:
        logger.info("Loading the Cached files...")
        train_df = pd.read_parquet(files[0])
        val_df = pd.read_parquet(files[1])
        test_df = pd.read_parquet(files[2])
        
        with open(files[3], 'r') as f:
            metadata = json.load(f)
            
        logger.info(f"Loaded sucessfully all the splits and the metadata, Train_df shape: {train_df.shape}, val_df shape: {val_df.shape}, test_df shape: {test_df.shape}")
        return (train_df, val_df, test_df, metadata)
    else:
        raise FileNotFoundError(f"One of the splits or the metadata file not found, Please check {path}")
        


@app.command()
def build(
    input_path: Path = RAW_DATA_PATH,
    output_path: Path = AFTER_EDA,
    force_rebuild: bool = typer.Option(
        False, "--force-rebuild", help="Skip cache and rebuild from scratch."
    ),
):
    build_dataset(
        raw_path=input_path,
        processed_dir=output_path,
        W=W,
        force_rebuild=force_rebuild,
    )
    
@app.command()
def validate():
    logger.info("Validating the pipeline...")
    exit_code = int(pytest.main(['tests/', '-v']))
    if not exit_code:
        logger.info("All tests passed!")
    else:
        raise typer.Exit(code=exit_code)


if __name__ == "__main__":
    app()
