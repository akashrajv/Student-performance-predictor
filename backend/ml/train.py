import pandas as pd
import numpy as np
import joblib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

from backend.config import settings
from backend.ml.preprocessing import PreprocessingPipeline
from backend.ml.evaluate import evaluate_classification_model
from backend.services.db_service import DatabaseService

def train_all_models(dataset_path: str = None) -> Dict[str, Any]:
    if dataset_path is None:
        dataset_path = str(settings.RAW_DATA_PATH)
        
    df = pd.read_csv(dataset_path)

    # 1. Determine Target Column
    target_col = None
    for cand in ['Performance_Level', 'Performance_Class', 'Target', 'Label']:
        if cand in df.columns:
            target_col = cand
            break
    if not target_col:
        target_col = df.columns[-1]

    # 1. Fit Preprocessing Pipeline
    pipeline = PreprocessingPipeline()
    pipeline.fit(df, target_col=target_col)
    
    # 2. Transform Features and Target
    X = pipeline.transform(df)
    y = pipeline.transform_target(df[target_col])
    classes = list(pipeline.label_encoder.classes_)
    feature_names = pipeline.feature_names

    # 3. Stratified Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # 4. Train Model 1: Logistic Regression with L2 Regularization independently
    print("Training Logistic Regression with L2 regularization independently...")
    lr_model = LogisticRegression(
        C=1.0,
        solver='lbfgs',
        max_iter=1000,
        random_state=42
    )
    lr_model.fit(X_train, y_train)

    # 5. Train Model 2: Random Forest independently
    print("Training Random Forest Classifier independently...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=4,
        random_state=42
    )
    rf_model.fit(X_train, y_train)

    # 6. Train Model 3: XGBoost independently
    print("Training XGBoost Classifier independently...")
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss'
    )
    xgb_model.fit(X_train, y_train)

    # 7. Compute Training Accuracies for all models
    lr_train_acc = float(accuracy_score(y_train, lr_model.predict(X_train)))
    rf_train_acc = float(accuracy_score(y_train, rf_model.predict(X_train)))
    xgb_train_acc = float(accuracy_score(y_train, xgb_model.predict(X_train)))

    # 8. Feature Importances Extraction
    # Random Forest importances
    rf_importances = dict(zip(feature_names, [round(float(v), 4) for v in rf_model.feature_importances_]))
    # XGBoost importances
    xgb_importances = dict(zip(feature_names, [round(float(v), 4) for v in xgb_model.feature_importances_]))
    # Logistic Regression mean absolute coefficient magnitude as normalized importance
    lr_coef_mag = np.mean(np.abs(lr_model.coef_), axis=0)
    lr_coef_normalized = lr_coef_mag / np.sum(lr_coef_mag) if np.sum(lr_coef_mag) > 0 else lr_coef_mag
    lr_importances = dict(zip(feature_names, [round(float(v), 4) for v in lr_coef_normalized]))

    # 9. Evaluate Models on Test Data
    lr_eval = evaluate_classification_model(lr_model, X_test, y_test, classes)
    rf_eval = evaluate_classification_model(rf_model, X_test, y_test, classes)
    xgb_eval = evaluate_classification_model(xgb_model, X_test, y_test, classes)

    # Attach training accuracy and feature importance to metrics
    lr_eval["train_accuracy"] = round(lr_train_acc, 4)
    lr_eval["feature_importance"] = lr_importances

    rf_eval["train_accuracy"] = round(rf_train_acc, 4)
    rf_eval["feature_importance"] = rf_importances

    xgb_eval["train_accuracy"] = round(xgb_train_acc, 4)
    xgb_eval["feature_importance"] = xgb_importances

    models_info = {
        "Logistic Regression": {
            "model": lr_model,
            "metrics": lr_eval,
            "filename": "logistic_regression.pkl"
        },
        "Random Forest": {
            "model": rf_model,
            "metrics": rf_eval,
            "filename": "random_forest.pkl"
        },
        "XGBoost": {
            "model": xgb_model,
            "metrics": xgb_eval,
            "filename": "xgboost.pkl"
        }
    }

    # 10. Compare All Models Accuracy Scores and Choose the one with Best Training Accuracy
    best_model_name = max(
        models_info.keys(),
        key=lambda m: models_info[m]["metrics"]["train_accuracy"]
    )
    best_model_obj = models_info[best_model_name]["model"]
    best_train_acc = models_info[best_model_name]["metrics"]["train_accuracy"]

    print("\n=== Model Accuracy Scores Comparison ===")
    comparison = []
    for m_name in sorted(models_info.keys(), key=lambda m: models_info[m]["metrics"]["train_accuracy"], reverse=True):
        m_eval = models_info[m_name]["metrics"]
        is_best = (m_name == best_model_name)
        m_eval["is_best_model"] = is_best
        comp_item = {
            "model_name": m_name,
            "train_accuracy": m_eval["train_accuracy"],
            "test_accuracy": m_eval["accuracy"],
            "accuracy_gap": round(abs(m_eval["train_accuracy"] - m_eval["accuracy"]), 4),
            "f1_score": m_eval["f1_score"],
            "precision": m_eval["precision"],
            "recall": m_eval["recall"],
            "is_best": is_best
        }
        comparison.append(comp_item)
        print(f"-> {m_name}: Train Acc = {m_eval['train_accuracy'] * 100:.2f}% | Test Acc = {m_eval['accuracy'] * 100:.2f}% | F1 = {m_eval['f1_score'] * 100:.2f}% {'[BEST SELECTED]' if is_best else ''}")

    print(f"\nChosen best model based on training accuracy: {best_model_name} ({best_train_acc * 100:.2f}%)\n")

    metrics = {
        "Logistic Regression": lr_eval,
        "Random Forest": rf_eval,
        "XGBoost": xgb_eval
    }

    # 11. Persist Model Artifacts
    settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    pipeline.save(settings.ARTIFACTS_DIR / "preprocessing.pkl")
    joblib.dump(lr_model, settings.ARTIFACTS_DIR / "logistic_regression.pkl")
    joblib.dump(rf_model, settings.ARTIFACTS_DIR / "random_forest.pkl")
    joblib.dump(xgb_model, settings.ARTIFACTS_DIR / "xgboost.pkl")
    # Persist chosen best model
    joblib.dump(best_model_obj, settings.ARTIFACTS_DIR / "best_model.pkl")

    # Clean up old ensemble artifact if present
    old_ensemble = settings.ARTIFACTS_DIR / "ensemble.pkl"
    if old_ensemble.exists():
        try:
            old_ensemble.unlink()
            print("Removed legacy ensemble.pkl artifact.")
        except Exception:
            pass

    # Save metrics JSON
    with open(settings.ARTIFACTS_DIR / "model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    best_model_info = {
        "best_model_name": best_model_name,
        "best_training_accuracy": best_train_acc,
        "test_accuracy": models_info[best_model_name]["metrics"]["accuracy"],
        "f1_score": models_info[best_model_name]["metrics"]["f1_score"],
        "comparison": comparison,
        "selected_criterion": "Best Training Accuracy",
        "timestamp": datetime.now().isoformat()
    }
    with open(settings.ARTIFACTS_DIR / "best_model_info.json", "w") as f:
        json.dump(best_model_info, f, indent=2)

    # 12. Save Metrics to Database
    DatabaseService.save_model_metrics(metrics)

    # 13. Seed First 150 students into the database for immediate exploration
    DatabaseService.save_students_batch(df.head(150).to_dict(orient='records'))

    print("Model training, accuracy comparison, best model selection, and artifact persistence completed successfully.")
    return {
        "dataset_records": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "models_evaluated": list(metrics.keys()),
        "best_model": best_model_name,
        "best_training_accuracy": best_train_acc,
        "comparison": comparison,
        "metrics": metrics,
        "classes": classes,
        "feature_names": feature_names,
        "trained_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    from backend.database.db import init_db
    init_db()
    res = train_all_models()
    print("Training Results Summary:")
    print(f"Selected Best Model: {res['best_model']} (Train Accuracy: {res['best_training_accuracy'] * 100:.2f}%)")
    for comp in res["comparison"]:
        print(f"-> {comp['model_name']}: Train Acc={comp['train_accuracy']} | Test Acc={comp['test_accuracy']} | F1={comp['f1_score']} | Best={comp['is_best']}")
