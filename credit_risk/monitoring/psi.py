import pandas as pd
import numpy as np
from credit_risk.features import (
    NUMERICAL_COLS,
    CATEGORICAL_COLS,
    prep_one_split
)

def psi_numeric(reference: pd.Series, target: pd.Series, bins=10) -> float:
    """Calculates the psi drift metric for a given feature

    Args:
        reference (pd.Series): reference distribution
        target (pd.Series): target distribution
        bins (int, optional): No of bins to create for both the distributions to compare and calculate psi. Defaults to 10.

    Returns:
        float: returns psi metric
    """
    quantiles = [i*(1/bins) for i in range(bins+1)]
    # print("Quantiles: ", quantiles)
    bin_boundary = np.nanquantile(reference, q=quantiles)
    bin_boundary[0] = -np.inf
    bin_boundary[-1] = np.inf
    
    reference_cuts = pd.cut(reference, bins=bin_boundary, duplicates='drop').value_counts()
    target_cuts = pd.cut(target, bins=bin_boundary, duplicates='drop').value_counts()
    
    interval_idx = reference_cuts.index.categories
    
    reference_cuts = reference_cuts.reindex(index=interval_idx, fill_value=0) / len(reference)
    target_cuts = target_cuts.reindex(index=interval_idx, fill_value=0) / len(target)
    
    # calculating the missing values 
    missing_ref = reference.isna().sum() / len(reference)
    missing_tar = target.isna().sum() / len(target)
    
    # changing the Interval Index dtype
    reference_cuts.index = reference_cuts.index.astype(str)
    target_cuts.index = target_cuts.index.astype(str)
    
    # Adding the 'missing' index
    reference_cuts['missing'] = missing_ref
    target_cuts['missing'] = missing_tar
    
    reference_cuts = reference_cuts.clip(lower=1e-4)
    target_cuts = target_cuts.clip(lower=1e-4)
    
    # print(reference_cuts)
    # print(target_cuts)
    
    psi_value = ((target_cuts - reference_cuts) * np.log(target_cuts.divide(reference_cuts))).sum()
    
    return psi_value.item()


def psi_categorical(reference: pd.Series, target: pd.Series) -> float:
    """Calculates the psi drift metric for a given feature

    Args:
        reference (pd.Series): reference distribution
        target (pd.Series): target distribution

    Returns:
        float: returns psi metric
    """
    
    reference_cuts = reference[reference.notna()].value_counts()
    target_cuts = target[target.notna()].value_counts()
    
    # unseen cat
    unseen = list(set(target_cuts.index) - set(reference_cuts.index))
    
    if unseen:
        unseen_data = target_cuts.loc[unseen].sum()
        target_cuts['unseen_category'] = unseen_data
        mask = [val for val in target_cuts.index if val not in unseen]
        target_cuts = target_cuts.loc[mask]
        reference_cuts['unseen_category'] = 0
        
    
    # missing vals
    missing_ref = reference.isna().sum()
    missing_tar = target.isna().sum()
    
    reference_cuts['missing'] = missing_ref
    target_cuts['missing'] = missing_tar
    
    # reindexing
    idx = reference_cuts.index
    reference_cuts = reference_cuts.reindex(index=idx, fill_value=0)
    target_cuts = target_cuts.reindex(index=idx, fill_value=0)
    
    reference_cuts /= len(reference)
    target_cuts  /= len(target)
    
    reference_cuts = reference_cuts.clip(lower=1e-4)
    target_cuts = target_cuts.clip(lower=1e-4)
    
    psi_value = ((target_cuts - reference_cuts) * np.log(target_cuts.divide(reference_cuts))).sum()
        
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
def build_drift_report(reference_df: pd.DataFrame, target_df: pd.DataFrame, target_label: str) -> pd.DataFrame:
    """Creates a complete covariate shift report using the PSI values

    Args:
        reference_df (pd.DataFrame): Reference Dataframe
        target_df (pd.DataFrame): Target Dataframe
        target_label (str): Target Dataframe Name

    Returns:
        pd.DataFrame: Drift Report Dataframe 
    """
    
    reference_df, _ = prep_one_split(df=reference_df)
    target_df, _ = prep_one_split(df=target_df)
    
    report = {
        'feature': [],
        'PSI': [],
        'drift_level': [],
        'target_label': [],
    }
    
    # Calculating PSI values for Numerical Columns
    for col in NUMERICAL_COLS:
        psi_val = psi_numeric(reference=reference_df[col], target=target_df[col])
        level = flag_level(psi_value=psi_val)
        
        report['feature'].append(col)
        report['PSI'].append(psi_val)
        report['drift_level'].append(level)
        report['target_label'].append(target_label)
        
    # Calculating PSI values for categorical Columns
    for col in CATEGORICAL_COLS:
        psi_val = psi_categorical(reference=reference_df[col], target=target_df[col])
        level = flag_level(psi_value=psi_val)
        
        report['feature'].append(col)
        report['PSI'].append(psi_val)
        report['drift_level'].append(level)
        report['target_label'].append(target_label)
        
    return pd.DataFrame(report)

# Summarize
def summarize_drift_report(report_df: pd.DataFrame) -> dict:
    """Summarizes the PSI report

    Args:
        report_df (pd.DataFrame): PSI Report
    """
    
    summary = {}
    
    summary['counts'] = pd.crosstab(report_df['target_label'], report_df['drift_level'])
    
    summary['flagged'] = report_df[report_df['drift_level'] != 'stable'].sort_values(by='PSI', ascending=False)
    
    return summary