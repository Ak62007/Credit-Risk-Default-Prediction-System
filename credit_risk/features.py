import joblib
import pytest
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

FEATURES_DIR = PROCESSED_DATA_DIR / 'features'
FEATURES_DIR.mkdir(parents=True, exist_ok=True)

DROP_COLS = ['inq_fi',
'sec_app_fico_range_low',
'annual_inc_joint',
'dti_joint',
'verification_status_joint',
'open_acc_6m',
'open_il_12m',
'open_il_24m',
'mths_since_rcnt_il',
'total_bal_il',
'il_util',
'open_rv_12m',
'open_rv_24m',
'max_bal_bc',
'all_util',
'total_cu_tl',
'inq_last_12m',
'revol_bal_joint',
'open_act_il',
'sec_app_fico_range_high',
'sec_app_inq_last_6mths',
'sec_app_mths_since_last_major_derog',
'sec_app_chargeoff_within_12_mths',
'sec_app_num_rev_accts',
'sec_app_open_act_il',
'sec_app_revol_util',
'sec_app_open_acc',
'sec_app_mort_acc',
'sec_app_collections_12_mths_ex_med',
'sec_app_earliest_cr_line',
'policy_code',
'issue_d',
'earliest_cr_line',
'fico_range_low',
'fico_range_high',
'application_type',
'disbursement_method',
'zip_code',
'title',
'desc',
'emp_title']

NUMERICAL_COLS = ['loan_amnt',
'funded_amnt',
'funded_amnt_inv',
'int_rate',
'installment',
'annual_inc',
'dti',
'delinq_2yrs',
'inq_last_6mths',
'mths_since_last_delinq',
'mths_since_last_record',
'open_acc',
'pub_rec',
'revol_bal',
'revol_util',
'total_acc',
'collections_12_mths_ex_med',
'mths_since_last_major_derog',
'acc_now_delinq',
'tot_coll_amt',
'tot_cur_bal',
'total_rev_hi_lim',
'acc_open_past_24mths',
'avg_cur_bal',
'bc_open_to_buy',
'bc_util',
'chargeoff_within_12_mths',
'delinq_amnt',
'mo_sin_old_il_acct',
'mo_sin_old_rev_tl_op',
'mo_sin_rcnt_rev_tl_op',
'mo_sin_rcnt_tl',
'mort_acc',
'mths_since_recent_bc',
'mths_since_recent_bc_dlq',
'mths_since_recent_inq',
'mths_since_recent_revol_delinq',
'num_accts_ever_120_pd',
'num_actv_bc_tl',
'num_actv_rev_tl',
'num_bc_sats',
'num_bc_tl',
'num_il_tl',
'num_op_rev_tl',
'num_rev_accts',
'num_rev_tl_bal_gt_0',
'num_sats',
'num_tl_120dpd_2m',
'num_tl_30dpd',
'num_tl_90g_dpd_24m',
'num_tl_op_past_12m',
'pct_tl_nvr_dlq',
'percent_bc_gt_75',
'pub_rec_bankruptcies',
'tax_liens',
'tot_hi_cred_lim',
'total_bal_ex_mort',
'total_bc_limit',
'total_il_high_credit_limit',
'credit_age_yrs',
'fico_mid'
]

CATEGORICAL_COLS = [
'term',
'grade',
'sub_grade',
'emp_length',
'home_ownership',
'verification_status',
'purpose',
'addr_state',
'initial_list_status'
]

def split_target_and_features(df: pd.DataFrame) -> list[pd.DataFrame, pd.Series]:
    """splits the target and the features from the data and returns it"""
    logger.info(f'Inside Function: {split_target_and_features.__name__}')
    logger.info('Splitting the target and the features...')
    target = df['target']
    n_df = df.drop(columns=['target'])
    logger.info("features and target are splitted successfully...")
    return n_df, target

def drop_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drops the unusable columns given in the DROP_COLS"""
    logger.info(f'Inside Function: {drop_columns.__name__}')
    logger.info('Drpping columns given un the DROP_COLS')
    n_df = df.drop(columns=DROP_COLS)
    logger.info("Dropped successfully!")
    return n_df

def add_credit_yrs(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a feature called credit_yrs"""
    logger.info(f'Inside Function: {add_credit_yrs.__name__}')
    assert ('issue_d' in df.columns) and ('earliest_cr_line' in df.columns)
    logger.info("Adding the feature 'credit_yrs'")
    df['credit_age_yrs'] = (df['issue_d'] - df['earliest_cr_line']).dt.days/365.25
    logger.info("'credit_age_yrs added successfully!'")
    return df

def add_fico_mid(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a feature called fico_mid"""
    logger.info(f'Inside Function: {add_fico_mid.__name__}')
    assert ('fico_range_low' in df.columns) and ('fico_range_high' in df.columns)
    logger.info("Adding the feature 'fico_mid'")
    df['fico_mid'] = (df['fico_range_low'] + df['fico_range_high'])/2
    logger.info("'fico_mid' added successfully!")
    return df    

def create_pipeline() -> tuple[Pipeline, Pipeline]:
    """Building pipeline for numeric and categorical features"""
    logger.info(f'Inside Function: {create_pipeline.__name__}')
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    logger.info('Pipeline created sucessfully...')
    return (numeric_pipeline, categorical_pipeline)

def building_preprocessor(num_pipeline: Pipeline, cat_pipeline: Pipeline) -> ColumnTransformer:
    """Building the complete preprocessor using the pipelines"""
    logger.info(f'Inside Function: {building_preprocessor.__name__}')
    logger.info(f"creating the preprocessor...")
    
    preprocessor = ColumnTransformer([
        ('num', num_pipeline, NUMERICAL_COLS),
        ('cat', cat_pipeline,CATEGORICAL_COLS),
    ], remainder='drop')
    
    logger.info('preprocessor created sucessfully!')
    return preprocessor

def prep_one_split(df: pd.DataFrame) -> tuple[np.array, np.array]:
    """Runs the whole pipeline before before transform"""
    logger.info(f'Inside Function: {prep_one_split.__name__}')
    features, target = split_target_and_features(df)
    features = add_credit_yrs(features)
    features = add_fico_mid(features)
    features = drop_columns(features)
    
    return features, target

def building_features(input_path: Path = AFTER_EDA, output_path: Path = FEATURES_DIR):
    """Complete feature creation pipeline in one function"""
    logger.info(f'Inside Function: {building_features.__name__}')
    train_df, val_df, test_df, _ = load_splits(path=input_path)
    logger.info(f"processing all the splits and saving them...")
    
    train_feat, y_train = prep_one_split(train_df)
    val_feat, y_val = prep_one_split(val_df)
    test_feat, y_test = prep_one_split(test_df)
    
    logger.info("fitting and learning the stats of train_df...")
    num_pipeline, cat_pipeline = create_pipeline()
    preprocessor = building_preprocessor(num_pipeline=num_pipeline, cat_pipeline=cat_pipeline)
    preprocessor.fit(train_feat)
    
    logger.info("Transforming all three splits on the learned stats of train_feat...")
    t_train_feat = preprocessor.transform(train_feat)
    t_val_feat = preprocessor.transform(val_feat)
    t_test_feat = preprocessor.transform(test_feat)
    
    logger.info("Saving the features...")    
    feature_names = preprocessor.get_feature_names_out()
    pd.DataFrame(t_train_feat, columns=feature_names).to_parquet(output_path / "train_features.parquet")
    pd.DataFrame(t_val_feat,   columns=feature_names).to_parquet(output_path / "val_features.parquet")
    pd.DataFrame(t_test_feat,  columns=feature_names).to_parquet(output_path / "test_features.parquet")
    
    logger.info("Saving the target...")
    y_train.to_frame().to_parquet(output_path / "train_target.parquet")
    y_val.to_frame().to_parquet(output_path / "val_target.parquet")
    y_test.to_frame().to_parquet(output_path / "test_target.parquet")
        
    logger.info("Saving the preprocessor...")
    joblib.dump(preprocessor, output_path / 'preprocessor.pkl')
    logger.info(f"Saved successfully at {output_path}")
    
def load_features(path: Path = FEATURES_DIR) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    """Loads the processed features"""
    logger.info("Loading the processed features...")
    train_feat = pd.read_parquet(path / "train_features.parquet")
    val_feat = pd.read_parquet(path / "val_features.parquet")
    test_feat = pd.read_parquet(path / "test_features.parquet")
    y_train  = pd.read_parquet(path / "train_target.parquet")
    y_val = pd.read_parquet(path / "val_target.parquet")
    y_test = pd.read_parquet(path / "test_target.parquet")
    logger.info("Loaded successfully!")
    return {
        'train': (train_feat, y_train),
        'val': (val_feat, y_val),
        'test': (test_feat, y_test)
    }


@app.command()
def build(
    input_path: Path = AFTER_EDA,
    output_path: Path = FEATURES_DIR,
):
    building_features(input_path=input_path, output_path=output_path)
    
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
