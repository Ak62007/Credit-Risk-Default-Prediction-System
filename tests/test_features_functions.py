import pytest
import pandas as pd
from credit_risk.features import (
    drop_columns,
    add_credit_yrs,
    add_fico_mid,
    sorting_with_issue_d,
    split_target_and_features
)

def test_drop_columns():
    t_drop_cols = ['funded_amnt_inv', 'grade']
    test_data = {
        'funded_amnt_inv': [200.0, 6000.0],
        'grade': ['A', 'B'],
        'annual_inc': [20000.0, 10000.0],
        'dti': [30.0, 20.0]
    }
    
    test_df = pd.DataFrame(data=test_data)
    
    t_data = drop_columns(df=test_df, drop_cols=t_drop_cols)
    
    assert set(t_data.columns) == {"annual_inc", "dti"}, (
        f"Function: {drop_columns.__name__} isn't dropping the given columns correctly!"
    )
    
    
def test_add_credit_yrs():
    test_data = {
        "issue_d": pd.to_datetime(["2011-12-31"]),
        "earliest_cr_line": pd.to_datetime(["2007-12-31"])
    }
    
    test_df = pd.DataFrame(test_data)
    
    t_data = add_credit_yrs(df=test_df)
    
    assert "credit_age_yrs" in t_data.columns, (
        f"Function: {add_credit_yrs.__name__}: credit_age_yrs is not added correctly!"
    )
    assert t_data['credit_age_yrs'].iloc[0] == pytest.approx(4.0), (
        f"Function: {add_credit_yrs.__name__}: credit_age_yrs is not calculated correctly!"
    )
    
def test_add_fico_mid():
    test_data = {
        "fico_range_low": [10.0],
        "fico_range_high": [30.0]
    }
    
    test_df = pd.DataFrame(test_data)
    
    t_data = add_fico_mid(df=test_df)
    
    assert "fico_mid" in t_data.columns, (
        f"Function: {add_fico_mid.__name__}: fico_mid is not added correctly!"
    )
    
    assert t_data['fico_mid'].iloc[0] == pytest.approx(20.0), (
        f"Function: {add_fico_mid.__name__}: fico_mid is not calculated correctly!"
    )
    
def test_sorting_with_issue_d():
    test_data = {
        "id": [1, 2, 3],
        "issue_d": pd.to_datetime(["2007-08-09", "2003-06-02", '2026-07-23']),
        "annual_inc": [2000.0, 4000.0, 10000.0]
    }
    
    test_df = pd.DataFrame(test_data)
    
    t_data = sorting_with_issue_d(test_df)
    
    assert t_data['issue_d'].is_monotonic_increasing, (
        f"Function: {sorting_with_issue_d.__name__} isn't sorting the data correctly"
    )
    
def test_split_target_and_features():
    test_data = {
        "target": [0, 1, 1],
        "annual_inc": [2000.0, 5000.0, 1200.0],
        "dti": [12.0, 1.2, 6.7]
    }
    
    test_df = pd.DataFrame(test_data)
    
    feat, target = split_target_and_features(df=test_df)
    
    assert set(feat.columns) == {"annual_inc", "dti"}, (
        f"Function: {split_target_and_features.__name__} isn't extracting the features correctly!"
    )
    
    assert set(target.unique()) == {0,1}, (
        f"Function: {split_target_and_features.__name__} isn't extracting the target correctly!"
    )