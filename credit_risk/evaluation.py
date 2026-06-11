import numpy as np
from typing import Any
from sklearn.metrics import (
    roc_auc_score,
    confusion_matrix,
    precision_score,
    recall_score,
    average_precision_score,
    brier_score_loss
)


def compute_metrics(y_true: np.array, y_proba: np.array, threshold: float) -> dict[str, Any]:
    """Returns a dict of all the calculated metrics"""
    y_pred = (y_proba >= threshold).astype(int)
    
    return {
        'ROC-AUC': roc_auc_score(y_true=y_true, y_score=y_proba),
        'PR-AUC': average_precision_score(y_true=y_true, y_score=y_proba),
        'brier_score': brier_score_loss(y_true=y_true, y_proba=y_proba),
        'precision': precision_score(y_true=y_true, y_pred=y_pred),
        'recall': recall_score(y_true=y_true, y_pred=y_pred),
        'confusion_matrix': confusion_matrix(y_true=y_true, y_pred=y_pred),
    }
    

def tune_threshold(y_true: np.array, y_proba: np.array, *, fn_cost: float, fp_cost: float) -> float:
    """tunes which threshold is best that minimizes the cost"""
    
    threshols = np.linspace(0.01, 0.99, 99)
    
    cost = []
    for thes in threshols:
        y_pred = (y_proba >= thes).astype(int)
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        fn = ((y_true == 1) & (y_pred == 0)).sum()
        cost.append((fp * fp_cost) + (fn * fn_cost))
        
    return threshols[np.argmin(cost)]

def evaluate_model(y_train, train_proba, y_val, val_proba, y_test, test_proba, *, fn_cost, fp_cost):
    t = tune_threshold(y_val, val_proba, fn_cost=fn_cost, fp_cost=fp_cost)
    return {
        "threshold": t,
        'train': compute_metrics(y_train, train_proba, t),
        "val": compute_metrics(y_val, val_proba, t),
        "test": compute_metrics(y_test, test_proba, t),
    }