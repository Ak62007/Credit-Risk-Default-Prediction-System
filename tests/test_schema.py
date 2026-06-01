"""Tier 1: schema validation.

These tests verify that loaded splits have the expected structure:
correct columns, correct dtypes, no unexpected nulls in critical columns.
They guard against upstream changes (vendor schema shift, code regression)
that would corrupt downstream feature engineering and modeling.
"""

import pytest
import pandas as pd

CHECKERS = {
    "datetime": pd.api.types.is_datetime64_any_dtype,
    "int":      pd.api.types.is_integer_dtype,
    "float":    pd.api.types.is_float_dtype,
    "string":   pd.api.types.is_string_dtype,
}

REQUIRED_COLUMNS = {
    "issue_d":                 "datetime",
    "target":                  "int",

    "loan_amnt":               "float",
    "term":                    "string",
    "purpose":                 "string",
    "title":                   "string",

    "annual_inc":              "float",
    "emp_length":              "string",  
    "emp_title":               "string",
    "home_ownership":          "string",
    "addr_state":              "string",
    "zip_code":                "string",
    "verification_status":     "string",
    "application_type":        "string",

    "fico_range_high":         "float",
    "fico_range_low":          "float",
    "earliest_cr_line":        "string", 
    "open_acc":                "float",
    "pub_rec":                 "float",
    "revol_bal":               "float",
    "revol_util":              "float",
    "total_acc":               "float",
    "dti":                     "float",
    "delinq_2yrs":             "float",
    "inq_last_6mths":          "float",
    "mths_since_last_delinq":  "float",
    "mths_since_last_record":  "float",
    "collections_12_mths_ex_med": "float",
    "pub_rec_bankruptcies":    "float",
    "tax_liens":               "float",
    "chargeoff_within_12_mths": "float",

    "num_sats":                "float",
    "num_actv_bc_tl":          "float",
    "num_tl_op_past_12m":      "float",
    "mo_sin_old_rev_tl_op":    "float",
    "mo_sin_rcnt_rev_tl_op":   "float",
    "bc_open_to_buy":          "float",
    "bc_util":                 "float",
    "il_util":                 "float",
    "open_il_24m":             "float",

    "annual_inc_joint":        "float",
    "dti_joint":               "float",
    "verification_status_joint": "string",

    "int_rate":                "float",     
    "grade":                   "string",       
    "sub_grade":               "string",       
    "installment":             "float",      
    "funded_amnt":             "float",      
    "acc_now_delinq":          "float",      
    "delinq_amnt":             "float",      
}

SEC_APP_FIELDS_NEVER_POPULATED = {
    "revol_bal_joint",
    "sec_app_fico_range_low", "sec_app_fico_range_high",
    "sec_app_earliest_cr_line", "sec_app_inq_last_6mths",
    "sec_app_mort_acc", "sec_app_open_acc", "sec_app_revol_util",
    "sec_app_open_act_il", "sec_app_num_rev_accts",
    "sec_app_chargeoff_within_12_mths",
    "sec_app_collections_12_mths_ex_med",
    "sec_app_mths_since_last_major_derog",
}

JOINT_AGGREGATE_FIELDS_TRAIN_ONLY = {
    "annual_inc_joint",
    "dti_joint",
    "verification_status_joint",
}

INSTALLMENT_TRACKER_TRAIN_ONLY = {
    "open_acc_6m", "open_act_il", "open_il_12m", "open_il_24m",
    "mths_since_rcnt_il", "total_bal_il", "il_util",
    "open_rv_12m", "open_rv_24m", "max_bal_bc", "all_util",
    "inq_fi", "total_cu_tl", "inq_last_12m",
}

ALLOWED_FULLY_NULL = {
    "train": (
        SEC_APP_FIELDS_NEVER_POPULATED
        | JOINT_AGGREGATE_FIELDS_TRAIN_ONLY
        | INSTALLMENT_TRACKER_TRAIN_ONLY
    ),
    "val":  SEC_APP_FIELDS_NEVER_POPULATED,
    "test": SEC_APP_FIELDS_NEVER_POPULATED,
}

def test_required_columns_present(train_df):
    """Tests of the columns mentioned in REQUIRED_COLUMNS are present in train_df"""
    required = set(REQUIRED_COLUMNS.keys())
    missing = required - set(train_df.columns)
    
    assert not missing, f"{len(missing)} columns are missing!"
    

def test_required_columns_dtypes(train_df):
    """Tests if the required columns have expected dtypes or not"""
    mis_matches = {}
    for col, expected_kind in REQUIRED_COLUMNS.items():
        checker = CHECKERS[expected_kind]
        
        if not checker(train_df[col]):
            mis_matches[col] = (expected_kind, str(train_df[col].dtype))
            
    assert not mis_matches, f"Dtype mismatches: {mis_matches}"
    
@pytest.mark.parametrize(
    'split_name',
    ['train', 'val', 'test']
)    
def test_target_has_no_nulls(split_name, splits):
    """Tests for all three splits if target column has no nulls"""
    df = splits[split_name]
    null_count = df['target'].isna().sum()
    
    assert null_count == 0, f"null count in {split_name}: {null_count}"
    
@pytest.mark.parametrize(
    "split_name",
    ['train', 'val', 'test']
)
def test_row_match_with_metadata(split_name, splits, metadata):
    """Checks if the metadata number of rows matches the actual data rows"""
    df = splits[split_name]
    actual = df.shape[0]
    expected = metadata["row_counts"][split_name]
    assert actual == expected, f"Row count mismatch for {split_name} data, expected: {expected}, Actual: {actual}"
    
@pytest.mark.parametrize(
    "split_name",
    ['train', 'val', 'test']
)
def test_target_is_binary(split_name, splits):
    """Checks if the target is binary for all three splits"""
    df = splits[split_name]
    actual = set(df['target'].unique())
    
    assert actual == {0,1}, f"{split_name} df has target with these values: {actual}"
    
@pytest.mark.parametrize(
    'split_name',
    ['train', 'val', 'test']
)
def test_no_leakage_columns_present(split_name, splits, metadata):
    """tests if no leakage columns are present in all three splits"""
    df = splits[split_name]
    leakage_columns = set(metadata['dropped_leakage_columns'])
    actual_columns = set(df.columns)
    present_leakage_columns = leakage_columns & actual_columns
    
    assert not present_leakage_columns, f"available_leakage_columns in {split_name} df are: {present_leakage_columns}"

@pytest.mark.parametrize(
    'split_name',
    ['train', 'val', 'test']
)
def test_no_unexpectedly_empty_columns(split_name, splits):
    """Fires only on NEW 100%-null columns; documented sparsity is exempt.

    A 100%-null column is normally a strong signal of upstream breakage.
    However, LendingClub's data has documented structural sparsity (joint-app
    columns pre-2015, sec_app columns never populated). Those are listed in
    ALLOWED_FULLY_NULL per split, so this test catches *new* sparsity
    (regression) without firing on existing sparsity (known fact).
    """
    df = splits[split_name]
    
    fully_null = set(df.columns[df.isna().all()])
    expected_null = ALLOWED_FULLY_NULL[split_name]
    
    unexpected = fully_null - expected_null
    
    assert not unexpected, (
        f"{split_name} df has unexpectedly fully-null columns: {unexpected}. "
        f"If these are known-sparse, add to ALLOWED_FULLY_NULL[{split_name!r}] "
        f"with a comment explaining why."
    )    