import os
import socket
import psycopg2
from loguru import logger
from psycopg2.extras import Json
from psycopg2.extensions import parse_dsn
from psycopg2.pool import ThreadedConnectionPool
from credit_risk.api.schemas import RequestModel

try:
    conn_str = os.getenv("PREDICTION_LOGS_DB_URI")
    host = parse_dsn(conn_str)["host"]
    ipv4 = socket.gethostbyname(host)
    conn_str_with_hostaddr = conn_str + f" hostaddr={ipv4}"
    pool = ThreadedConnectionPool(minconn=1, maxconn=5, dsn=conn_str_with_hostaddr)
except Exception as e:
    logger.error(
        f"Failed to create prediction_logs connection pool or failed to get the PREDICTION_LOGS_DB_URI env var: {e}"
    )
    pool = None

RAW_INPUT_COLUMNS = [
    "loan_amnt",
    "installment",
    "annual_inc",
    "dti",
    "delinq_2yrs",
    "inq_last_6mths",
    "open_acc",
    "pub_rec",
    "revol_bal",
    "revol_util",
    "total_acc",
    "collections_12_mths_ex_med",
    "acc_now_delinq",
    "tot_coll_amt",
    "tot_cur_bal",
    "total_rev_hi_lim",
    "acc_open_past_24mths",
    "avg_cur_bal",
    "bc_open_to_buy",
    "bc_util",
    "chargeoff_within_12_mths",
    "delinq_amnt",
    "mo_sin_old_il_acct",
    "mo_sin_old_rev_tl_op",
    "mo_sin_rcnt_rev_tl_op",
    "mo_sin_rcnt_tl",
    "mort_acc",
    "num_accts_ever_120_pd",
    "num_actv_bc_tl",
    "num_actv_rev_tl",
    "num_bc_sats",
    "num_bc_tl",
    "num_il_tl",
    "num_op_rev_tl",
    "num_rev_accts",
    "num_rev_tl_bal_gt_0",
    "num_sats",
    "num_tl_120dpd_2m",
    "num_tl_30dpd",
    "num_tl_90g_dpd_24m",
    "num_tl_op_past_12m",
    "pct_tl_nvr_dlq",
    "percent_bc_gt_75",
    "pub_rec_bankruptcies",
    "tax_liens",
    "tot_hi_cred_lim",
    "total_bal_ex_mort",
    "total_bc_limit",
    "total_il_high_credit_limit",
    "fico_range_low",
    "fico_range_high",
    "mths_since_last_delinq",
    "mths_since_last_record",
    "mths_since_last_major_derog",
    "mths_since_recent_bc",
    "mths_since_recent_bc_dlq",
    "mths_since_recent_inq",
    "mths_since_recent_revol_delinq",
    "earliest_cr_line",
    "term",
    "emp_length",
    "home_ownership",
    "verification_status",
    "purpose",
    "addr_state",
    "initial_list_status",
]


def log_predictions(
    issue_d, req: RequestModel, req_id: str, pred: int, prob: float, reason_codes: dict
):
    """Logs the request and it's output in the RDS Database

    Args:
        req (dict): Raw request data
        req_id (str): request id
        pred (int): prediction output of the model
        prob (float): predicted probability of the model
        reason_codes (dict): SHAP reason codes
    """
    if pool is None:
        raise RuntimeError("Prediction log DB pool is unavailable")

    with logger.contextualize(request_id=req_id):
        conn = pool.getconn()
        cur = conn.cursor()

        sql = """
            INSERT INTO prediction_logs (
            request_id, issue_d,
            loan_amnt, installment, annual_inc, dti, delinq_2yrs, inq_last_6mths, open_acc, pub_rec,
            revol_bal, revol_util, total_acc, collections_12_mths_ex_med, acc_now_delinq, tot_coll_amt,
            tot_cur_bal, total_rev_hi_lim, acc_open_past_24mths, avg_cur_bal, bc_open_to_buy, bc_util,
            chargeoff_within_12_mths, delinq_amnt, mo_sin_old_il_acct, mo_sin_old_rev_tl_op,
            mo_sin_rcnt_rev_tl_op, mo_sin_rcnt_tl, mort_acc, num_accts_ever_120_pd, num_actv_bc_tl,
            num_actv_rev_tl, num_bc_sats, num_bc_tl, num_il_tl, num_op_rev_tl, num_rev_accts,
            num_rev_tl_bal_gt_0, num_sats, num_tl_120dpd_2m, num_tl_30dpd, num_tl_90g_dpd_24m,
            num_tl_op_past_12m, pct_tl_nvr_dlq, percent_bc_gt_75, pub_rec_bankruptcies, tax_liens,
            tot_hi_cred_lim, total_bal_ex_mort, total_bc_limit, total_il_high_credit_limit,
            fico_range_low, fico_range_high,
            mths_since_last_delinq, mths_since_last_record, mths_since_last_major_derog,
            mths_since_recent_bc, mths_since_recent_bc_dlq, mths_since_recent_inq, mths_since_recent_revol_delinq,
            earliest_cr_line,
            term, emp_length, home_ownership, verification_status, purpose, addr_state, initial_list_status,
            pred, prob, reason_codes
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s
            )
        """

        d = req.model_dump()
        values = (
            req_id,
            issue_d,
            *(d[col] for col in RAW_INPUT_COLUMNS),
            pred,
            prob,
            Json(reason_codes),
        )

        bad_conn = False
        try:
            cur.execute(sql, values)
            conn.commit()

        except Exception as e:
            bad_conn = True
            logger.error(f"Database error: {e}")
            raise

        else:
            logger.info("Query executed successfully")

        finally:
            cur.close()
            pool.putconn(conn, close=bad_conn)
