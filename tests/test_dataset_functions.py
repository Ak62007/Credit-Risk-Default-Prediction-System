import pandas as pd
from credit_risk.dataset import (
    drop_leakage_columns,
    build_target,
    STATUS_TO_LABEL,
    make_splits,
    compute_snapshot_date,
    apply_observation_window
)

def test_drop_leakage_columns():
    test_data = {
        "annual_inc": [20000.0, 5000.0, 200.0],
        "total_pymnt": [2000.0, 4000.0, 6000.0],
        "addr_state": ['CA', 'VA', 'SA'],
        "hardship_amount": [45000, 2000.0, 1000.0]
    }
    test_df = pd.DataFrame(data=test_data)
    
    f_data = drop_leakage_columns(test_df)
    
    assert set(f_data.columns) == {"annual_inc", "addr_state"}, (
        f"The function {drop_leakage_columns.__name__} isn't dropping the leakage features correctly!"
    )
    
def test_build_target():
    labels = list(STATUS_TO_LABEL.values())
    test_data = {
        "loan_status": list(STATUS_TO_LABEL.keys())
    }
    
    test_df = pd.DataFrame(data=test_data)
    
    f_data = build_target(test_df)
    
    assert "target" in f_data.columns and "loan_status" not in f_data.columns, (
        f"Target column is not formed or loan_status is not dropped!"
    )
    assert f_data['target'].to_list() == [val for val in labels if val is not None], (
        "Labels were not correctly assigned by the build_target function, or It dropped wrong rows"
    )
    
def test_make_splits():
    test_data = {
    "id": [1, 2, 3, 4, 5, 6],
    "issue_d": pd.to_datetime([
        "2007-01-01",
        "2014-12-31",
        "2015-06-15",
        "2016-06-15",
        "2006-12-31",
        "2017-01-01",
    ]),
    "target": [0, 1, 0, 1, 0, 1],
    }

    test_df = pd.DataFrame(data=test_data)
    
    train_df, val_df, test_df = make_splits(test_df)
    
    assert (train_df['id'].to_list() == [1,2] and
            val_df['id'].to_list() == [3] and
            test_df['id'].to_list() == [4]), (
                f"Function: {make_splits.__name__} isn't making the splits correctly!"
    )

    excluded_ids = {5, 6}
    all_split_ids = set(train_df['id']) | set(val_df['id']) | set(test_df['id'])
    assert excluded_ids.isdisjoint(all_split_ids), (
        f"Function: {make_splits.__name__} is leaking out-of-range rows "
        f"(ids {excluded_ids & all_split_ids}) into a split!"
    )

def test_apply_observation_window():
    test_data = {
        "id": [1, 2, 3, 4, 5],
        "issue_d": pd.to_datetime(["2007-06-11", "2023-08-12", "2015-09-16", "2025-08-01", "2026-07-23"]),
        "annual_inc": [30000.0, 2000.0, 112890.0, 78880.0, 34000.0]
    }
    
    test_df = pd.DataFrame(test_data)
    
    ss_date = compute_snapshot_date(test_df)
    
    t_data_1 = apply_observation_window(data=test_df, W=24, ss_date=ss_date)
    
    t_data_2 = apply_observation_window(data=test_df, W=9, ss_date=ss_date)
    
    assert ss_date == pd.to_datetime("2026-07-23"), (
        f"Function: {compute_snapshot_date.__name__} isn't calculating the screenshot date correctly!"
    )
    
    assert t_data_1['id'].to_list() == [1, 2, 3], (
        f"Function: {apply_observation_window.__name__} isn't filtering rows correctly!"
    )
    
    assert t_data_2['id'].to_list() == [1, 2, 3, 4], (
            f"Function: {apply_observation_window.__name__} isn't filtering rows correctly!"
    )