import pytest
import pandas as pd
import numpy as np

from credit_risk.monitoring.psi import psi_categorical, psi_numeric, flag_level

def test_numeric_same_distribution():
    reference = pd.Series(np.random.standard_normal(100))
    psi_value = psi_numeric(reference=reference, target=reference.copy())
    
    assert psi_value == pytest.approx(0.0), (
        f"{psi_numeric.__name__} is not giving psi value = 0.0 as output for calculating psi value for a same distribution"
    )
    
def test_cat_same_distribution():
    reference = pd.Series(['oyee', 'oyeeee', 'oyeeeeee'])
    psi_value = psi_categorical(reference=reference, target=reference.copy())
    
    assert psi_value == pytest.approx(0.0), (
        f"{psi_categorical.__name__} is not giving psi value = 0.0 as output for calculating psi value for a same distribution"
    )
    
def test_numeric_diff_distribution():
    reference = pd.Series(np.random.normal(loc=0, scale=1, size=1000))
    target = pd.Series(np.random.normal(loc=5, scale=1, size=1000))
    
    psi_value = psi_numeric(reference=reference, target=target)
    
    assert psi_value >= 0.1, (
        f"{psi_numeric.__name__} is not giving psi value >= 0.1 as output for calculating psi value for a different distribution"
    )

def test_cat_diff_distribution():
    reference = pd.Series(['A']*50 + ['B']*50)
    target = pd.Series(['A']*40 + ['B']*40 + ['C']*20)

    psi_value = psi_categorical(reference=reference, target=target)
    
    assert psi_value >= 0.1, (
        f"{psi_categorical.__name__} is not giving psi value >= 0.1 as output for calculating psi value for a different distribution"
    )
    
def test_numeric_missing_distribution():
    reference = pd.Series(np.arange(100).astype(float))
    target = reference.copy()
    
    reference.iloc[np.arange(2)] = np.nan
    target.iloc[np.arange(20)] = np.nan
    
    psi_value = psi_numeric(reference=reference, target=target)
    
    assert psi_value >= 0.1, (
        f"{psi_numeric.__name__} is not giving psi value >= 0.1 as output for calculating psi value for a distribution with missing values"
    )
    
def test_cat_missing_distribution():
    reference = pd.Series(['A']*50 + ['B']*50)
    target = pd.Series(['A']*40 + ['B']*40 + ['C']*20)
    
    reference.iloc[np.arange(2)] = np.nan
    target.iloc[np.arange(10)] = np.nan

    psi_value = psi_categorical(reference=reference, target=target)

    assert psi_value >= 0.1, (
        f"{psi_categorical.__name__} is not giving psi value >= 0.1 as output for calculating psi value for a distribution with missing values"
    )


def test_numeric_duplicate_edges_no_crash():
    reference = pd.Series([0.0] * 90 + [1.0] * 10)
    target = pd.Series([0.0] * 80 + [1.0] * 20)

    psi_value = psi_numeric(reference=reference, target=target)

    assert isinstance(psi_value, float), (
        f"{psi_numeric.__name__} should return a float without crashing on a zero-inflated/duplicate-edge feature"
    )


def test_numeric_bins_param_changes_result():
    reference = pd.Series(np.random.normal(loc=0, scale=1, size=1000))
    target = pd.Series(np.random.normal(loc=5, scale=1, size=1000))

    psi_5 = psi_numeric(reference=reference, target=target, bins=5)
    psi_10 = psi_numeric(reference=reference, target=target, bins=10)

    assert psi_5 != psi_10, (
        f"{psi_numeric.__name__} is producing the same PSI value regardless of the 'bins' argument"
    )


def test_cat_vanishing_category():
    reference = pd.Series(['A'] * 40 + ['B'] * 40 + ['C'] * 20)
    target = pd.Series(['A'] * 50 + ['B'] * 50)

    psi_value = psi_categorical(reference=reference, target=target)

    assert psi_value >= 0.1, (
        f"{psi_categorical.__name__} is not giving psi value >= 0.1 when a reference category vanishes entirely from target"
    )


def test_flag_level_stable():
    assert flag_level(0.05) == "stable"


def test_flag_level_moderate_boundary():
    assert flag_level(0.1) == "moderate"


def test_flag_level_significant():
    assert flag_level(0.3) == "significant"