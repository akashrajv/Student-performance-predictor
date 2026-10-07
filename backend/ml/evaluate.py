import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)

def evaluate_classification_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    classes: List[str]
) -> Dict[str, Any]:
    y_pred = model.predict(X_test)
    
    # Calculate probabilities if model supports predict_proba
    has_proba = hasattr(model, "predict_proba")
    y_proba = model.predict_proba(X_test) if has_proba else None

    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
    rec_macro = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average='macro', zero_division=0))
    
    prec_weighted = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
    rec_weighted = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_list = cm.tolist()

    # ROC-AUC calculation (multiclass OvR)
    roc_auc = None
    if has_proba and len(classes) > 2:
        try:
            roc_auc = float(roc_auc_score(y_test, y_proba, multi_class='ovr', average='macro'))
        except Exception:
            roc_auc = None
    elif has_proba and len(classes) == 2:
        try:
            roc_auc = float(roc_auc_score(y_test, y_proba[:, 1]))
        except Exception:
            roc_auc = None

    # Per-class breakdown
    per_class = {}
    for idx, c in enumerate(classes):
        # binary metrics for class c
        c_true = (y_test == idx).astype(int)
        c_pred = (y_pred == idx).astype(int)
        per_class[str(c)] = {
            "precision": round(float(precision_score(c_true, c_pred, zero_division=0)), 3),
            "recall": round(float(recall_score(c_true, c_pred, zero_division=0)), 3),
            "f1": round(float(f1_score(c_true, c_pred, zero_division=0)), 3),
            "support": int(np.sum(c_true))
        }

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec_weighted, 4),
        "recall": round(rec_weighted, 4),
        "f1_score": round(f1_weighted, 4),
        "precision_macro": round(prec_macro, 4),
        "recall_macro": round(rec_macro, 4),
        "f1_score_macro": round(f1_macro, 4),
        "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
        "confusion_matrix": cm_list,
        "classes": [str(c) for c in classes],
        "per_class": per_class
    }
