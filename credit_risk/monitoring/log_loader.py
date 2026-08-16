import os

from loguru import logger
import pandas as pd
import psycopg2

NULLABLE_NUMERIC_COLS = [
    "mths_since_last_delinq",
    "mths_since_last_record",
    "mths_since_last_major_derog",
    "mths_since_recent_bc",
    "mths_since_recent_bc_dlq",
    "mths_since_recent_inq",
    "mths_since_recent_revol_delinq",
]


def load_prediction_logs() -> pd.DataFrame:

    logger.info("Starting to load the prediction logs from prediction_logs table...")
    conn_str = os.getenv("MONITORING_READER_DB_URI")

    logger.info("Connecting to the DB...")
    conn = psycopg2.connect(conn_str)
    logger.info("Connection Successfull!")

    try:
        logger.info("Trying to read the logs...")
        df = pd.read_sql("SELECT * FROM prediction_logs", conn)
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    else:
        logger.info("Read the logs successfully!")
    finally:
        conn.close()

    # Creating the target placeholder
    logger.info("Adding the target place holder...")
    df["target"] = pd.NA

    # Correcting the date dtypes
    logger.info("Correcting the Date dtype features...")
    df["issue_d"] = pd.to_datetime(df["issue_d"])
    df["earliest_cr_line"] = pd.to_datetime(df["earliest_cr_line"])

    logger.info("Correcting the potential null features dtypes...")
    for col in NULLABLE_NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
