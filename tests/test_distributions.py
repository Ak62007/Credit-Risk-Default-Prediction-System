import pytest

@pytest.mark.parametrize('split_name', ['train', 'val', 'test'])
def test_dti_extreme_outliers_below_threshold(split_name, splits):
    """At most 1% of rows have dti > 100 (sentinel/error values).
    
    LendingClub's data has known dti=9999 sentinels indicating
    'not computed'. We tolerate up to 1% of rows being affected;
    a spike above that indicates upstream corruption.
    """
    df = splits[split_name]
    extreme = (df['dti'].dropna() > 100).mean()
    assert extreme < 0.01, (
        f"{split_name}: {extreme*100:.2f}% of rows have dti > 100 "
        f"(threshold 1%). Investigate sentinel handling upstream."
    )
    
@pytest.mark.parametrize('split_name', ['train', 'val', 'test'])
def test_default_rate_in_expected_band(split_name, splits):
    """Each split's default rate is within a plausible band [10%, 25%].
    
    Wider band than current observed rates (16-18%) to allow for
    moderate drift without false alarms. A rate outside this band
    indicates either the labeling logic broke or the data composition
    changed materially.
    """
    df = splits[split_name]
    rate = df['target'].mean()
    assert 0.10 <= rate <= 0.25, (
        f"{split_name}: default rate {rate:.3f} outside expected band [0.10, 0.25]"
    )