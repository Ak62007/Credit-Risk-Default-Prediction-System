import pandas as pd

from credit_risk.dataset import AFTER_EDA
from credit_risk.monitoring.log_loader import load_prediction_logs

from app import config
from app.services.cache import TTLCache


def _load_reference_df() -> pd.DataFrame:
    # Only the train split is ever used as the drift-comparison reference.
    # Uses a 40k-row random sample of the full 466k-row training set, not
    # the full set itself -- PSI's quantile-bucket comparisons don't need
    # every historical row to be statistically stable, and the full set's
    # ~839MB in-memory footprint was the main cause of repeated OOM kills
    # on this deployment box's limited RAM (see M22 note). Regenerate via:
    # df.sample(n=40000, random_state=42).to_parquet(...) on the full set.
    return pd.read_parquet(AFTER_EDA / "training_reference_sample.parquet")


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
