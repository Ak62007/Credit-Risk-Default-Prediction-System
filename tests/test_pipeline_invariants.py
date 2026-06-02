import pytest
import pandas as pd


def test_splits_are_temporally_ordered(train_df, val_df, test_df):
    """Checks if the splits are temporally aligned or not"""
    assert (max(train_df['issue_d']) < min(val_df['issue_d'])) and (max(val_df['issue_d']) < min(test_df['issue_d'])), (
        "All three splits are not temporally aligned."
    )
    
def test_splits_are_disjoint(train_df, val_df, test_df):
    """Checks if the three splits are disjoint or not"""
    combined = pd.concat([train_df, val_df, test_df], ignore_index=True)
    duplicates = combined.duplicated()
    assert not duplicates.any(), (
        f"{duplicates.sum()} rows appear in multiple splits"
    )
    
def test_rows_match_before_after_split(train_df, val_df, test_df, metadata):
    """Checks if the sum no of rows in the three splits is equal to the no of rows before split"""
    assert len(train_df) + len(val_df) + len(test_df) == metadata['row_count_before_split'], (
        "Some unknown rows are deleted while spliting, no of rows doesn't match"
    )
    
@pytest.mark.parametrize(
    "split_name",
    ['train', 'val', 'test']
)
def test_term_segment_default_rates_are_ordered(split_name, splits):
    """Checks if the long term loans have more default rate than the short term loans"""
    df = splits[split_name]
    default_rates = df.groupby(by="term")['target'].mean()
    
    assert default_rates[' 36 months'] < default_rates[' 60 months'], (
        f"The data shows long term loans does not have more default rate than the short term loans for {split_name} df"
    )