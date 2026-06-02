"""Tier 2: value validation.

These tests verify that values within columns are within expected bounds
and obey known invariants. They guard against data corruption, upstream
unit changes, sentinel values escaping into the data, and distribution
drift.
"""

import pytest
import pandas as pd
import numpy as np

NUMERIC_RANGES = {
    "loan_amnt":       (500, 50_000),
    "int_rate":        (0, 35),
    "fico_range_low":  (300, 850),
    "fico_range_high": (300, 850),
    "annual_inc":      (0, None),
}

CATEGORICAL_VALUES = {
    'term':                 {' 36 months', ' 60 months'},
    'grade':                {'A', 'C', 'D', 'B', 'E', 'F', 'G'},
    'sub_grade':            {'A3', 'C1', 'C3', 'D4', 'D1', 'C4', 'B5', 'D5', 'B4', 'E5', 'D2', 'B3', 'C5',
                             'C2', 'E4', 'B2', 'E3', 'A5', 'D3', 'B1', 'F1', 'A4', 'E1', 'G2', 'E2', 'A1',
                             'F2', 'A2', 'F3', 'G1', 'G3', 'F4', 'G4', 'F5', 'G5'},
    'emp_length':           {'8 years', '10+ years', '< 1 year', '6 years', '2 years', '7 years',
                             '9 years', '3 years', '4 years', '5 years', '1 year'},
    
    'home_ownership':       {'MORTGAGE', 'RENT', 'OWN', 'ANY', 'OTHER', 'NONE'},
    'verification_status':  {'Not Verified', 'Source Verified', 'Verified'},
    'purpose':              {'credit_card', 'debt_consolidation', 'car', 'home_improvement', 'house',
                             'other', 'medical', 'moving', 'major_purchase', 'vacation','small_business',
                             'renewable_energy', 'wedding','educational'},
    'addr_state':           {'AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI',
                             'IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN',
                             'MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH',
                             'OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA',
                             'WI','WV','WY'},
    'initial_list_status':  {'w', 'f'},
    'application_type':     {'Individual', 'Joint App'},
    'disbursement_method':  {'Cash', 'DirectPay'}
}

@pytest.mark.parametrize(
    "split_name",
    ['train', 'val', 'test']
)
@pytest.mark.parametrize(
    "col_name, bounds",
    list(NUMERIC_RANGES.items())
)
def test_ranges_of_columns(split_name, splits, col_name, bounds):
    """Tests if the columns values lies within reasonable range"""
    df = splits[split_name]
    feature = df[col_name].dropna()
    
    lo, hi = bounds
    check = pd.Series([False]*len(feature), index=feature.index)
    if lo is not None:
        check |= feature < lo
        
    if hi is not None:
        check |= feature > hi
        
    violating_values = feature[check]
    
    assert violating_values.empty, (
        f"{split_name}.{col_name}: {len(violating_values)} values out of "
        f"range {bounds}. Min={feature.min()}, max={feature.max()}, "
        f"sample violators: {violating_values.head(5).tolist()}"
    )
        
        
@pytest.mark.parametrize(
    'split_name',
    ['train', 'val', 'test']
)
@pytest.mark.parametrize(
    ('col_name', 'exp_values'),
    list(CATEGORICAL_VALUES.items())
)
def test_values_of_categorical_cols(split_name, splits, col_name,  exp_values):
    """Tests if the values in the categorical columns are known ones"""
    
    df = splits[split_name]
    feature = df[col_name].dropna()
    actual_vals = set(feature.unique())
    
    assert actual_vals.issubset(exp_values), (
        f"for {split_name} df anf for the column {col_name}, It has following new values that it takes: {actual_vals - exp_values}"
    )

@pytest.mark.parametrize(
    'split_name',
    ['train', 'val', 'test']
)    
def test_fico_low_and_high(split_name, splits):
    """Checks of all the 'fico_range_low' is lower than 'fico_range_high'"""
    df = splits[split_name]
    mask = df['fico_range_low'].notna() & df['fico_range_high'].notna()
    both_present = df[mask]
    assert (both_present['fico_range_low'] <= both_present['fico_range_high']).all(), (
        f"Inconsistent NULL values in one of the fico columns in {split_name} df."
    )
        
@pytest.mark.parametrize(
    'split_name',
    ['train', 'val', 'test']
)
def test_fund_amnt_less_loan_amnt(split_name, splits):
    """Checks if all the funded amount is less that loan amount"""
    df = splits[split_name]
    mask = df['funded_amnt'].notna() & df['loan_amnt'].notna()

    assert (df['funded_amnt'][mask] <= df['loan_amnt'][mask]).all(), (
        f"Not all the funded amnt in {split_name} df is less than it's corresponding loan_amnt"
    )
    

    
