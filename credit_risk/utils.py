import numpy as np
from typing import Literal
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

def to_jsonable(metrics: dict) -> dict:
    out = {}
    for key in metrics.keys():
        intermediate = {}
        if isinstance(metrics[key], dict):
            for k, v in metrics[key].items():
                if isinstance(v, np.ndarray):
                    intermediate[k] = v.tolist()
                elif isinstance(v, (np.floating, np.integer)):
                    intermediate[k] = v.item()
                else:
                    intermediate[k] = v
        else:
            if isinstance(metrics[key], (np.floating, np.integer)):
                out[key] = metrics[key].item()
            continue        
        out[key] = intermediate
    return out

def train(X_train: np.array, y_train: np.array, X_val: np.array, X_test: np.array, model: Literal['LR', 'RF', 'XGB']) -> tuple[np.array, np.array, np.array]:
    """trains the three models on the given data and returns the trained models"""
    if model == 'LR':
        lr_model = LogisticRegression()
        lr_model.fit(X=X_train, y=y_train)
        
        train_proba = lr_model.predict_proba(X_train)[:, 1]
        val_proba = lr_model.predict_proba(X_val)[:, 1]
        test_proba = lr_model.predict_proba(X_test)[:, 1]
        
        return (train_proba, val_proba, test_proba)
    
    elif model == 'RF':
        rf_model = RandomForestClassifier(n_jobs=-1, random_state=42)
        rf_model.fit(X=X_train, y=y_train)
        
        train_proba = rf_model.predict_proba(X_train)[:, 1]
        val_proba = rf_model.predict_proba(X_val)[:, 1]
        test_proba = rf_model.predict_proba(X_test)[:, 1]
        
        return (train_proba, val_proba, test_proba)
    
    elif model == 'XGB':
        xgb_model = XGBClassifier(n_jobs=-1, eval_metric='logloss')
        xgb_model.fit(X=X_train, y=y_train)
        
        train_proba = xgb_model.predict_proba(X_train)[:, 1]
        val_proba = xgb_model.predict_proba(X_val)[:, 1]
        test_proba = xgb_model.predict_proba(X_test)[:, 1]
        
        return (train_proba, val_proba, test_proba)
    
    else:
        raise ValueError('Invalid model!')
    
    