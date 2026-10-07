import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.ml.preprocessing import PreprocessingPipeline
from backend.ml.explain import explain_individual_prediction

MODEL_FILES = {
    "Logistic Regression": "logistic_regression.pkl",
    "Random Forest": "random_forest.pkl",
    "XGBoost": "xgboost.pkl",
    "Best Model": "best_model.pkl"
}

class PredictionEngine:
    _pipeline = None
    _models = {}
    _metrics = None
    _best_model_info = None

    @classmethod
    def get_pipeline(cls) -> PreprocessingPipeline:
        if cls._pipeline is None:
            pipeline_path = settings.ARTIFACTS_DIR / "preprocessing.pkl"
            if not pipeline_path.exists():
                raise FileNotFoundError("Model artifacts not found. Please train models first using the Model Training page.")
            cls._pipeline = PreprocessingPipeline.load(pipeline_path)
        return cls._pipeline

    @classmethod
    def get_best_model_info(cls) -> Dict[str, Any]:
        if cls._best_model_info is None:
            info_path = settings.ARTIFACTS_DIR / "best_model_info.json"
            if info_path.exists():
                try:
                    with open(info_path, "r") as f:
                        cls._best_model_info = json.load(f)
                except Exception:
                    pass
            if cls._best_model_info is None:
                # Compute dynamically from metrics
                metrics = cls.get_metrics()
                if metrics:
                    candidates = {k: v for k, v in metrics.items() if "train_accuracy" in v}
                    if candidates:
                        best_k = max(candidates.keys(), key=lambda k: candidates[k].get("train_accuracy", 0))
                        cls._best_model_info = {
                            "best_model_name": best_k,
                            "best_training_accuracy": candidates[best_k].get("train_accuracy", 0),
                            "test_accuracy": candidates[best_k].get("accuracy", 0),
                            "f1_score": candidates[best_k].get("f1_score", 0),
                        }
            if cls._best_model_info is None:
                cls._best_model_info = {
                    "best_model_name": "XGBoost",
                    "best_training_accuracy": 0.0
                }
        return cls._best_model_info

    @classmethod
    def get_model(cls, model_name: str = "Best Model"):
        best_info = cls.get_best_model_info()
        best_name = best_info.get("best_model_name", "XGBoost")

        normalized = model_name.strip() if model_name else "Best Model"
        if normalized in ["Best Model", "best", "auto", "default", "Ensemble", "ensemble"] or normalized.startswith("Best Model"):
            canonical_name = best_name
            target_key = "Best Model"
        elif "logistic" in normalized.lower():
            canonical_name = "Logistic Regression"
            target_key = canonical_name
        elif "forest" in normalized.lower():
            canonical_name = "Random Forest"
            target_key = canonical_name
        elif "xgb" in normalized.lower():
            canonical_name = "XGBoost"
            target_key = canonical_name
        else:
            canonical_name = best_name
            target_key = "Best Model"
            
        if canonical_name not in cls._models:
            filename = MODEL_FILES.get(target_key, MODEL_FILES.get(canonical_name, "best_model.pkl"))
            model_path = settings.ARTIFACTS_DIR / filename
            if not model_path.exists():
                # Fallback to model's own pickle or best_model.pkl
                fallback_filename = MODEL_FILES.get(canonical_name, "best_model.pkl")
                model_path = settings.ARTIFACTS_DIR / fallback_filename
                if not model_path.exists():
                    raise FileNotFoundError(f"Model file {filename} not found in artifacts. Please train models first.")
            cls._models[canonical_name] = joblib.load(model_path)
        return cls._models[canonical_name], canonical_name

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        if cls._metrics is None:
            metrics_path = settings.ARTIFACTS_DIR / "model_metrics.json"
            if metrics_path.exists():
                with open(metrics_path, "r") as f:
                    data = json.load(f)
                    # Filter out any legacy ensemble
                    cls._metrics = {k: v for k, v in data.items() if "ensemble" not in k.lower()}
            else:
                cls._metrics = {}
        return cls._metrics

    @classmethod
    def reload_artifacts(cls):
        cls._pipeline = None
        cls._models = {}
        cls._metrics = None
        cls._best_model_info = None

    @classmethod
    def predict_single(cls, student_data: Dict[str, Any], model_name: str = "XGBoost") -> Dict[str, Any]:
        if model_name and model_name.strip().lower() in ["model consensus", "consensus"]:
            from backend.ml.consensus import predict_consensus
            return predict_consensus(student_data)

        pipeline = cls.get_pipeline()
        model, canonical_name = cls.get_model(model_name)
        metrics = cls.get_metrics()

        # Dynamically format input dataframe using pipeline's active feature set
        row = {}
        for col in pipeline.numerical_cols:
            val = student_data.get(col)
            if val is None:
                for k, v in student_data.items():
                    if k.lower().replace("_", "") == col.lower().replace("_", ""):
                        val = v
                        break
            if val is None:
                # Fallback cross-mappings between schema variations
                if col == "Previous_Semester_CGPA":
                    prev = student_data.get("Previous_Grade") or student_data.get("previous_grade")
                    if prev is not None:
                        val = float(prev) / 10.0
                elif col == "Study_Hours_Per_Day":
                    hrs = student_data.get("Study_Hours_Per_Week") or student_data.get("study_hours_per_week")
                    if hrs is not None:
                        val = float(hrs) / 7.0
                elif col == "Internal_Marks":
                    val = student_data.get("Assessment_Score") or student_data.get("assessment_score")
                elif col == "Quiz_Score":
                    val = student_data.get("Participation_Score") or student_data.get("participation_score")
                elif col == "Previous_Backlogs":
                    val = student_data.get("Tutoring_Sessions") or student_data.get("tutoring_sessions") or 0
                elif col == "Practical_Marks":
                    val = student_data.get("Assignment_Score") or student_data.get("assignment_score")
                elif col == "Study_Hours_Per_Week":
                    d = student_data.get("Study_Hours_Per_Day") or student_data.get("study_hours_per_day")
                    if d is not None:
                        val = float(d) * 7.0
                elif col == "Previous_Grade":
                    cgpa = student_data.get("Previous_Semester_CGPA") or student_data.get("previous_semester_cgpa")
                    if cgpa is not None:
                        val = float(cgpa) * 10.0

            if val is None:
                val = pipeline.feature_stats.get(col, {}).get("median", 50.0)
            try:
                row[col] = float(val)
            except (ValueError, TypeError):
                row[col] = float(pipeline.feature_stats.get(col, {}).get("median", 50.0))

        for col in pipeline.categorical_cols:
            val = student_data.get(col)
            if val is None:
                for k, v in student_data.items():
                    if k.lower().replace("_", "") == col.lower().replace("_", ""):
                        val = v
                        break
            if val is None:
                val = "No" if "Extra" in col else ("Yes" if "Internet" in col else "Bachelor")
            row[col] = str(val)

        df_input = pd.DataFrame([row])
        X_trans = pipeline.transform(df_input)

        # Predict
        predicted_idx = model.predict(X_trans)[0]
        classes = list(pipeline.label_encoder.classes_)
        predicted_class = str(pipeline.inverse_transform_target([predicted_idx])[0])

        # Probabilities
        probabilities = {}
        confidence = None
        if hasattr(model, "predict_proba"):
            try:
                probs = model.predict_proba(X_trans)[0]
                for idx, c in enumerate(classes):
                    probabilities[str(c)] = round(float(probs[idx]), 4)
                confidence = round(float(np.max(probs)), 4)
            except Exception:
                confidence = None
        else:
            confidence = None

        # Calculate Risk Category and Risk Score (0-100%)
        # Supports both Poor/Average/Good/Excellent and Low/Medium/High
        prob_poor = probabilities.get("Poor", probabilities.get("Low", 0.0))
        prob_avg = probabilities.get("Average", probabilities.get("Medium", 0.0))
        prob_good = probabilities.get("Good", 0.0)
        prob_exc = probabilities.get("Excellent", probabilities.get("High", 0.0))

        if probabilities:
            risk_score = round(float((prob_poor * 1.0 + prob_avg * 0.45 + prob_good * 0.10) * 100.0), 1)
        else:
            # Fallback if model has no probabilities
            if predicted_class in ["Poor", "Low"]:
                risk_score = 75.0
            elif predicted_class in ["Average", "Medium"]:
                risk_score = 45.0
            else:
                risk_score = 15.0

        if prob_poor >= 0.35 or risk_score >= 50.0 or predicted_class in ["Poor", "Low"]:
            risk_category = "High Risk"
        elif prob_avg >= 0.40 or risk_score >= 25.0 or predicted_class in ["Average", "Medium"]:
            risk_category = "Moderate Risk"
        else:
            risk_category = "Low Risk"

        # Feature importances for this model
        model_metric_key = canonical_name
        feat_importances = metrics.get(model_metric_key, {}).get("feature_importance", {})

        # Contributing factors for explainable AI
        contributing_factors = explain_individual_prediction(
            student_dict=row,
            pipeline=pipeline,
            model_name=canonical_name,
            feature_importances=feat_importances,
            predicted_class=predicted_class
        )

        student_id = str(student_data.get("student_id") or student_data.get("Student_ID", "STU-NEW"))
        student_name = str(student_data.get("name") or student_data.get("Name", "Student"))

        return {
            "student_id": student_id,
            "student_name": student_name,
            "model_used": canonical_name,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "risk_category": risk_category,
            "risk_score": risk_score,
            "probabilities": probabilities,
            "contributing_factors": contributing_factors,
            "input_data": row
        }

    @classmethod
    def predict_with_all_models(cls, student_data: Dict[str, Any]) -> Dict[str, Any]:
        from backend.ml.consensus import predict_with_all_models
        return predict_with_all_models(student_data)

    @classmethod
    def predict_consensus(cls, student_data: Dict[str, Any]) -> Dict[str, Any]:
        from backend.ml.consensus import predict_consensus
        return predict_consensus(student_data)

