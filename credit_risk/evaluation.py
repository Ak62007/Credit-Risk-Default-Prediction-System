import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    f1_score,
    confusion_matrix,
    precision_score,
    recall_score,
    average_precision_score,
    brier_score_loss
)


def compute_metrics(y_true: np.array, y_proba: np.array, threshold: float) -> dict[str, any]:
    """Returns a dict of all the calculated metrics"""
    y_pred = (y_proba >= threshold).astype(int)
    
    return {
        'ROC-AUC': roc_auc_score(y_true=y_true, y_score=y_proba),
        'PR-AUC': average_precision_score(y_true=y_true, y_score=y_proba),
        'brier_score': brier_score_loss(y_true=y_true, y_proba=y_proba),
        'precision': precision_score(y_true=y_true, y_pred=y_pred),
        'recall': recall_score(y_true=y_true, y_pred=y_pred),
        'confusion_matrix': confusion_matrix(y_true=y_true, y_pred=y_pred),
        'accuracy': accuracy_score(y_true=y_true, y_pred=y_pred),
        'f1score': f1_score(y_true=y_true, y_pred=y_pred),   
    }
    

def tune_threshold(y_true: np.array, y_proba: np.array, fn_cost: float, fp_cost: float) -> float:
    """tunes which threshold is best that minimizes the cost"""
    
    threshols = np.linspace(0.01, 0.99, 99)
    
    cost = []
    for thes in threshols:
        y_pred = (y_proba >= thes).astype(int)
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        fn = ((y_true == 1) & (y_pred == 0)).sum()
        cost.append((fp * fp_cost) + (fn * fn_cost))
        
    return threshols[np.argmin(cost)]

