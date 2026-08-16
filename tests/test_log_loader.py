from unittest.mock import MagicMock

import pandas as pd
import pytest

import credit_risk.monitoring.log_loader as loader


def _fake_raw_df(**overrides) -> pd.DataFrame:
    """A minimal stand-in for what pd.read_sql would return from
    `SELECT * FROM prediction_logs` -- just the columns load_prediction_logs()
    actually touches, so tests aren't coupled to the full 70+ column schema.
    """
    n = 3
    data = {
        "request_id": [f"req-{i}" for i in range(n)],
        "issue_d": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "earliest_cr_line": ["1998-03-01", "2001-06-15", "2005-11-20"],
        # all-None column -- regression test for the dtype bug where an all-None
        # column read via pd.read_sql on a raw DBAPI2 connection came back as
        # object dtype holding raw None instead of float64/NaN.
        "mths_since_last_delinq": [None, None, None],
        # mixed None/value column -- must preserve the real values, not just
        # convert everything to NaN.
        "mths_since_recent_inq": [None, 4.0, 12.0],
    }
    # any remaining NULLABLE_NUMERIC_COLS not explicitly set above, filled with None
    for col in loader.NULLABLE_NUMERIC_COLS:
        if col not in data:
            data[col] = [None] * n
    data.update(overrides)
    return pd.DataFrame(data)


@pytest.fixture
def mock_db(monkeypatch):
    """Replaces psycopg2.connect and pd.read_sql inside log_loader so no test
    ever touches the real database. Returns (mock_conn, fake_df) so tests can
    assert on connection lifecycle.
    """
    mock_conn = MagicMock()
    fake_df = _fake_raw_df()

    monkeypatch.setattr(loader.psycopg2, "connect", MagicMock(return_value=mock_conn))
    monkeypatch.setattr(loader.pd, "read_sql", MagicMock(return_value=fake_df.copy()))
    monkeypatch.setenv("MONITORING_READER_DB_URI", "postgresql://fake/dsn")

    return mock_conn, fake_df


def test_adds_target_column_as_na(mock_db):
    df = loader.load_prediction_logs()
    assert "target" in df.columns
    assert df["target"].isna().all()


def test_converts_date_columns_to_datetime(mock_db):
    df = loader.load_prediction_logs()
    assert pd.api.types.is_datetime64_any_dtype(df["issue_d"])
    assert pd.api.types.is_datetime64_any_dtype(df["earliest_cr_line"])


def test_all_none_column_becomes_float_not_object(mock_db):
    df = loader.load_prediction_logs()
    # this is the exact bug found earlier: an all-None column read via pd.read_sql
    # on a raw DBAPI2 connection silently became object dtype holding raw Python
    # None, which broke pd.cut() downstream in build_drift_report().
    assert pd.api.types.is_float_dtype(df["mths_since_last_delinq"])
    assert df["mths_since_last_delinq"].isna().all()


def test_mixed_column_preserves_real_values(mock_db):
    df = loader.load_prediction_logs()
    assert pd.api.types.is_float_dtype(df["mths_since_recent_inq"])
    values = df["mths_since_recent_inq"].tolist()
    assert pd.isna(values[0])
    assert values[1:] == [4.0, 12.0]


def test_all_nullable_numeric_cols_converted_to_float(mock_db):
    df = loader.load_prediction_logs()
    for col in loader.NULLABLE_NUMERIC_COLS:
        assert pd.api.types.is_float_dtype(df[col]), f"{col} was not converted to float dtype"


def test_closes_connection_on_success(mock_db):
    mock_conn, _ = mock_db
    loader.load_prediction_logs()
    mock_conn.close.assert_called_once()


def test_closes_connection_and_reraises_on_db_error(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr(loader.psycopg2, "connect", MagicMock(return_value=mock_conn))
    monkeypatch.setattr(loader.pd, "read_sql", MagicMock(side_effect=RuntimeError("query failed")))
    monkeypatch.setenv("MONITORING_READER_DB_URI", "postgresql://fake/dsn")

    with pytest.raises(RuntimeError, match="query failed"):
        loader.load_prediction_logs()

    mock_conn.close.assert_called_once()
