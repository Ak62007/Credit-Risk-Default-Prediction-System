from unittest.mock import MagicMock

import pytest

import credit_risk.monitoring.prediction_logger as plog
from credit_risk.api.schemas import RequestModel


@pytest.fixture
def sample_request(raw_input) -> RequestModel:
    return RequestModel(**raw_input)


@pytest.fixture
def mock_pool(monkeypatch):
    """Replaces the module-level `pool` with a mock, so no test ever touches
    the real database. `getconn()` returns a mock connection whose `.cursor()`
    returns a mock cursor -- both are returned so tests can assert on them.
    """
    mock_cur = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur

    mock_pool_obj = MagicMock()
    mock_pool_obj.getconn.return_value = mock_conn

    monkeypatch.setattr(plog, "pool", mock_pool_obj)
    return mock_pool_obj, mock_conn, mock_cur


def _call_log_predictions(sample_request, **overrides):
    kwargs = dict(
        issue_d="2026-01-01",
        req=sample_request,
        req_id="abc-123",
        pred=0,
        prob=0.1,
        reason_codes={"dti": 0.1},
    )
    kwargs.update(overrides)
    return plog.log_predictions(**kwargs)


def test_raises_if_pool_is_none(monkeypatch, sample_request):
    monkeypatch.setattr(plog, "pool", None)

    with pytest.raises(RuntimeError, match="unavailable"):
        _call_log_predictions(sample_request)


def test_values_tuple_length_matches_sql_placeholders(mock_pool, sample_request):
    _, _, mock_cur = mock_pool

    _call_log_predictions(sample_request)

    sql, values = mock_cur.execute.call_args[0]
    placeholder_count = sql.count("%s")
    assert len(values) == placeholder_count, (
        "values tuple passed to cur.execute() doesn't have one entry per %s "
        "placeholder in the SQL -- this exact mismatch caused a real bug earlier "
        "in the project (69 placeholders vs 71 columns)"
    )


def test_values_tuple_matches_column_count(mock_pool, sample_request):
    _, _, mock_cur = mock_pool

    _call_log_predictions(sample_request)

    sql, values = mock_cur.execute.call_args[0]
    column_count = sql.split("INSERT INTO prediction_logs (")[1].split(") VALUES")[0].count(",") + 1
    assert len(values) == column_count


def test_values_start_with_request_id_and_issue_d(mock_pool, sample_request):
    _, _, mock_cur = mock_pool

    _call_log_predictions(sample_request, req_id="req-xyz", issue_d="2026-02-14")

    _, values = mock_cur.execute.call_args[0]
    assert values[0] == "req-xyz"
    assert values[1] == "2026-02-14"


def test_values_end_with_pred_prob_reason_codes(mock_pool, sample_request):
    _, _, mock_cur = mock_pool

    _call_log_predictions(sample_request, pred=1, prob=0.77, reason_codes={"dti": 0.2})

    _, values = mock_cur.execute.call_args[0]
    assert values[-3] == 1
    assert values[-2] == 0.77
    # reason_codes is wrapped in psycopg2.extras.Json before going into the tuple --
    # .adapted holds the original dict it was constructed with.
    assert values[-1].adapted == {"dti": 0.2}


def test_raw_input_values_pulled_in_correct_order(mock_pool, sample_request, raw_input):
    _, _, mock_cur = mock_pool

    _call_log_predictions(sample_request)

    _, values = mock_cur.execute.call_args[0]
    raw_values = values[2:-3]  # everything between issue_d and pred
    assert len(raw_values) == len(plog.RAW_INPUT_COLUMNS)
    for col, value in zip(plog.RAW_INPUT_COLUMNS, raw_values):
        assert value == raw_input[col], f"mismatch for column '{col}'"


def test_commits_and_returns_healthy_connection_on_success(mock_pool, sample_request):
    mock_pool_obj, mock_conn, mock_cur = mock_pool

    _call_log_predictions(sample_request)

    mock_conn.commit.assert_called_once()
    mock_cur.close.assert_called_once()
    mock_pool_obj.putconn.assert_called_once_with(mock_conn, close=False)


def test_discards_connection_and_reraises_on_db_error(mock_pool, sample_request):
    mock_pool_obj, mock_conn, mock_cur = mock_pool
    mock_cur.execute.side_effect = RuntimeError("connection reset")

    with pytest.raises(RuntimeError, match="connection reset"):
        _call_log_predictions(sample_request)

    mock_conn.commit.assert_not_called()
    mock_cur.close.assert_called_once()
    # this is the actual bug fixed earlier: a failed connection must be discarded
    # (close=True), not silently recycled back into the pool for the next caller.
    mock_pool_obj.putconn.assert_called_once_with(mock_conn, close=True)
