from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.services.db_service import DatabaseService
from backend.ml.predict import PredictionEngine

router = APIRouter(prefix="/api", tags=["Models"])

@router.get("/models")
async def get_models():
    best_info = PredictionEngine.get_best_model_info()
    best_name = best_info.get("best_model_name", "XGBoost")
    best_train_acc = best_info.get("best_training_accuracy", 0.0)

    return {
        "best_model": best_name,
        "best_training_accuracy": best_train_acc,
        "selection_criterion": "Best Training Accuracy",
        "models": [
            {
                "id": "Logistic Regression",
                "name": "Logistic Regression (L2 Regularized)",
                "description": "Independently trained linear model with L2 (Ridge) penalty to prevent overfitting on collinear student features and provide calibrated probabilities.",
                "type": "Linear / Regularized Baseline",
                "regularization": "L2 Regularization (Ridge)",
                "is_best": (best_name == "Logistic Regression")
            },
            {
                "id": "Random Forest",
                "name": "Random Forest Classifier",
                "description": "Independently trained ensemble of de-correlated decision trees capturing nonlinear interactions between attendance, study habits, and grades.",
                "type": "Bagging Ensemble (Decision Trees)",
                "n_estimators": 100,
                "is_best": (best_name == "Random Forest")
            },
            {
                "id": "XGBoost",
                "name": "XGBoost Classifier",
                "description": "Independently trained gradient boosted trees minimizing loss residuals with high predictive performance.",
                "type": "Boosting (Extreme Gradient Boosting)",
                "n_estimators": 100,
                "is_best": (best_name == "XGBoost")
            }
        ]
    }

@router.get("/model-metrics")
async def get_model_metrics():
    # Attempt to load from Database first, fallback to artifacts
    metrics = DatabaseService.get_latest_metrics()
    if not metrics:
        metrics = PredictionEngine.get_metrics()
        
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="No model metrics found. Please train models first using the Model Training page."
        )
    
    # Filter out any legacy ensemble entries
    filtered_metrics = {k: v for k, v in metrics.items() if "ensemble" not in k.lower()}
    best_info = PredictionEngine.get_best_model_info()

    return {
        "status": "success",
        "best_model": best_info.get("best_model_name"),
        "best_training_accuracy": best_info.get("best_training_accuracy"),
        "comparison": best_info.get("comparison", []),
        "selection_criterion": "Best Training Accuracy",
        "models": filtered_metrics
    }
