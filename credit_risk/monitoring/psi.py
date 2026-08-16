from loguru import logger
import numpy as np
import pandas as pd
import typer

from credit_risk.config import REPORTS_DIR
from credit_risk.dataset import AFTER_EDA, load_splits
from credit_risk.features import CATEGORICAL_COLS, NUMERICAL_COLS, prep_one_split

app = typer.Typer()

OUTPUT_DIR = REPORTS_DIR / "drift"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def psi_numeric(reference: pd.Series, target: pd.Series, bins=10) -> float:
    """Calculates the psi drift metric for a given feature

    Args:
        reference (pd.Series): reference distribution
        target (pd.Series): target distribution
        bins (int, optional): No of bins to create for both the distributions to compare and calculate psi. Defaults to 10.

    Returns:
        float: returns psi metric
    """
    feature_name = reference.name or "unnamed_feature"
    logger.info(f"[psi_numeric] Calculating PSI for '{feature_name}' with {bins} requested bins")

    quantiles = [i * (1 / bins) for i in range(bins + 1)]
    # print("Quantiles: ", quantiles)
    bin_boundary = np.nanquantile(reference, q=quantiles)
    bin_boundary[0] = -np.inf
    bin_boundary[-1] = np.inf

    reference_cuts = pd.cut(reference, bins=bin_boundary, duplicates="drop").value_counts()
    target_cuts = pd.cut(target, bins=bin_boundary, duplicates="drop").value_counts()

    interval_idx = reference_cuts.index.categories
    if len(interval_idx) < bins:
        logger.info(
            f"[psi_numeric] '{feature_name}': duplicate bin edges collapsed {bins} requested "
            f"bins down to {len(interval_idx)} actual bins"
        )

    reference_cuts = reference_cuts.reindex(index=interval_idx, fill_value=0) / len(reference)
    target_cuts = target_cuts.reindex(index=interval_idx, fill_value=0) / len(target)

    # calculating the missing values
    missing_ref = reference.isna().sum() / len(reference)
    missing_tar = target.isna().sum() / len(target)

    # changing the Interval Index dtype
    reference_cuts.index = reference_cuts.index.astype(str)
    target_cuts.index = target_cuts.index.astype(str)

    # Adding the 'missing' index
    reference_cuts["missing"] = missing_ref
    target_cuts["missing"] = missing_tar

    reference_cuts = reference_cuts.clip(lower=1e-4)
    target_cuts = target_cuts.clip(lower=1e-4)

    # print(reference_cuts)
    # print(target_cuts)

    psi_value = ((target_cuts - reference_cuts) * np.log(target_cuts.divide(reference_cuts))).sum()

    logger.info(f"[psi_numeric] '{feature_name}': PSI = {psi_value.item():.4f}")

    return psi_value.item()


def psi_categorical(reference: pd.Series, target: pd.Series) -> float:
    """Calculates the psi drift metric for a given feature

    Args:
        reference (pd.Series): reference distribution
        target (pd.Series): target distribution

    Returns:
        float: returns psi metric
    """

    feature_name = reference.name or "unnamed_feature"
    logger.info(f"[psi_categorical] Calculating PSI for '{feature_name}'")

    reference_cuts = reference[reference.notna()].value_counts()
    target_cuts = target[target.notna()].value_counts()

    # unseen cat
    unseen = list(set(target_cuts.index) - set(reference_cuts.index))

    if unseen:
        logger.info(
            f"[psi_categorical] '{feature_name}': found {len(unseen)} unseen category value(s) in target: {unseen}"
        )
        unseen_data = target_cuts.loc[unseen].sum()
        target_cuts["unseen_category"] = unseen_data
        mask = [val for val in target_cuts.index if val not in unseen]
        target_cuts = target_cuts.loc[mask]
        reference_cuts["unseen_category"] = 0

    # missing vals
    missing_ref = reference.isna().sum()
    missing_tar = target.isna().sum()
    if missing_ref or missing_tar:
        logger.info(
            f"[psi_categorical] '{feature_name}': missing counts - reference={missing_ref}, target={missing_tar}"
        )

    reference_cuts["missing"] = missing_ref
    target_cuts["missing"] = missing_tar

    # reindexing
    idx = reference_cuts.index
    reference_cuts = reference_cuts.reindex(index=idx, fill_value=0)
    target_cuts = target_cuts.reindex(index=idx, fill_value=0)

    reference_cuts /= len(reference)
    target_cuts /= len(target)

    reference_cuts = reference_cuts.clip(lower=1e-4)
    target_cuts = target_cuts.clip(lower=1e-4)

    psi_value = ((target_cuts - reference_cuts) * np.log(target_cuts.divide(reference_cuts))).sum()

    logger.info(f"[psi_categorical] '{feature_name}': PSI = {psi_value.item():.4f}")

    return psi_value.item()


# Helper Function
def flag_level(psi_value: float) -> str:
    if psi_value < 0.1:
        return "stable"
    elif 0.1 <= psi_value < 0.25:
        return "moderate"
    else:
        return "significant"


# Create The Report
def build_drift_report(
    reference_df: pd.DataFrame, target_df: pd.DataFrame, target_label: str
) -> pd.DataFrame:
    """Creates a complete covariate shift report using the PSI values

    Args:
        reference_df (pd.DataFrame): Reference Dataframe
        target_df (pd.DataFrame): Target Dataframe
        target_label (str): Target Dataframe Name

    Returns:
        pd.DataFrame: Drift Report Dataframe
    """

    logger.info(
        f"[build_drift_report] target_label='{target_label}': processing "
        f"{len(NUMERICAL_COLS)} numeric + {len(CATEGORICAL_COLS)} categorical features"
    )

    reference_df, _ = prep_one_split(df=reference_df)
    target_df, _ = prep_one_split(df=target_df)

    report = {
        "feature": [],
        "PSI": [],
        "drift_level": [],
        "target_label": [],
    }

    # Calculating PSI values for Numerical Columns
    for col in NUMERICAL_COLS:
        psi_val = psi_numeric(reference=reference_df[col], target=target_df[col])
        level = flag_level(psi_value=psi_val)

        report["feature"].append(col)
        report["PSI"].append(psi_val)
        report["drift_level"].append(level)
        report["target_label"].append(target_label)

    # Calculating PSI values for categorical Columns
    for col in CATEGORICAL_COLS:
        psi_val = psi_categorical(reference=reference_df[col], target=target_df[col])
        level = flag_level(psi_value=psi_val)

        report["feature"].append(col)
        report["PSI"].append(psi_val)
        report["drift_level"].append(level)
        report["target_label"].append(target_label)

    report_df = pd.DataFrame(report)
    flagged_counts = report_df["drift_level"].value_counts().to_dict()
    logger.info(
        f"[build_drift_report] target_label='{target_label}': done, flag counts = {flagged_counts}"
    )

    return report_df


# Summarize
def summarize_drift_report(report_df: pd.DataFrame) -> dict:
    """Summarizes the PSI report

    Args:
        report_df (pd.DataFrame): PSI Report
    """

    summary = {}

    summary["counts"] = pd.crosstab(report_df["target_label"], report_df["drift_level"])

    summary["flagged"] = report_df[report_df["drift_level"] != "stable"].sort_values(
        by="PSI", ascending=False
    )

    return summary


def orchestrator():
    """Creates the PSI report and summary for train as reference and val and test set as target distributions"""
    logger.info(f"[orchestrator] Loading train/val/test splits from {AFTER_EDA}")
    train_df, val_df, test_df, _ = load_splits(path=AFTER_EDA)

    train_val_psi = build_drift_report(reference_df=train_df, target_df=val_df, target_label="val")
    train_test_psi = build_drift_report(
        reference_df=train_df, target_df=test_df, target_label="test"
    )

    report = pd.concat([train_val_psi, train_test_psi], ignore_index=True)

    output_path = OUTPUT_DIR / "drift_report.csv"
    report.to_csv(path_or_buf=output_path, index=False)
    logger.info(f"[orchestrator] Saved drift report ({len(report)} rows) to {output_path}")


@app.command(name="check")
def run_drift_check_on_splits():
    orchestrator()


if __name__ == "__main__":
    app()
