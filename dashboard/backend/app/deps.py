import pandas as pd

from credit_risk.dataset import AFTER_EDA, load_splits
from credit_risk.monitoring.log_loader import load_prediction_logs

from app import config
from app.services.cache import TTLCache


def _load_reference_df() -> pd.DataFrame:
    train_df, _val_df, _test_df, _metadata = load_splits(path=AFTER_EDA)
    return train_df


# Reference (training) data never changes at runtime -> cached for the process lifetime.
_reference_cache: TTLCache[pd.DataFrame] = TTLCache(_load_reference_df, ttl_seconds=None)

# Live prediction logs -> short TTL so a page load firing several requests shares one DB round trip.
_live_cache: TTLCache[pd.DataFrame] = TTLCache(load_prediction_logs, ttl_seconds=config.LIVE_DF_CACHE_TTL_SECONDS)


def get_reference_df() -> pd.DataFrame:
    return _reference_cache.get()


def get_live_df() -> pd.DataFrame:
    return _live_cache.get()


def live_df_loaded_at() -> float | None:
    return _live_cache.loaded_at()


def reference_loaded() -> bool:
    return _reference_cache.loaded_at() is not None
