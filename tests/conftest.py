import pytest
import pandas as pd

from credit_risk.dataset import load_splits
from credit_risk.config import PROCESSED_DATA_DIR

@pytest.fixture(scope='session')
def splits():
    """Load (train, val, test, metadata) once for the entire test session."""
    train_df, val_df, test_df, metadata = load_splits(path=PROCESSED_DATA_DIR / "after_eda")
    return {
        'train': train_df,
        'val': val_df,
        'test': test_df,
        'metadata': metadata,
    }
    
@pytest.fixture(scope='session')
def train_df(splits):
    return splits['train']


@pytest.fixture(scope='session')
def val_df(splits):
    return splits['val']


@pytest.fixture(scope="session")
def test_df(splits):
    return splits["test"]


@pytest.fixture(scope="session")
def metadata(splits):
    return splits["metadata"]