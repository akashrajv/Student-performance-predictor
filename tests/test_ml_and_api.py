import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import os
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.preprocessing import PreprocessingPipeline
from backend.ml.predict import PredictionEngine
from backend.llm.explanation import generate_grounded_fallback

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_trained"] is True

def test_models_list_endpoint():
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "best_model" in data
    assert data["best_model"] in ["Logistic Regression", "Random Forest", "XGBoost"]
    assert "best_training_accuracy" in data
    model_ids = [m["id"] for m in data["models"]]
    assert "Logistic Regression" in model_ids
    assert "Random Forest" in model_ids
    assert "XGBoost" in model_ids
    # Ensure Ensemble is NOT used or present
    assert "Ensemble" not in model_ids
    assert len(model_ids) == 3

def test_model_metrics_endpoint():
    response = client.get("/api/model-metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "best_model" in data
    assert "best_training_accuracy" in data
    assert "comparison" in data
    models = data["models"]
    # Ensure Ensemble is NOT in metrics
    assert "Ensemble" not in models
    assert "Ensemble (Voting)" not in models
    for m in ["Logistic Regression", "Random Forest", "XGBoost"]:
        assert m in models
        assert "train_accuracy" in models[m]
        assert "accuracy" in models[m]
        assert "f1_score" in models[m]
        assert "confusion_matrix" in models[m]
        assert "feature_importance" in models[m]

def test_single_prediction_endpoint():
    payload = {
        "student": {
            "student_id": "TEST_001",
            "name": "Test High Performer",
            "attendance_percentage": 96.0,
            "study_hours_per_week": 26.0,
            "previous_grade": 89.0,
            "assignment_score": 92.0,
            "assessment_score": 90.0,
            "participation_score": 88.0,
            "sleep_hours": 7.5,
            "tutoring_sessions": 2,
            "extracurricular_activities": "Yes",
            "parental_education": "Master",
            "internet_access": "Yes"
        },
        "model_name": "XGBoost"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["predicted_class"] in ["High", "Medium", "Low", "Poor", "Average", "Good", "Excellent"]
    assert res["risk_category"] in ["Low Risk", "Moderate Risk", "High Risk"]
    assert 0.0 <= res["confidence"] <= 1.0
    assert 0.0 <= res["risk_score"] <= 100.0
    assert len(res["contributing_factors"]) > 0

def test_at_risk_student_prediction():
    payload = {
        "student": {
            "student_id": "TEST_RISK",
            "name": "Struggling Student",
            "attendance_percentage": 50.0,
            "study_hours_per_week": 4.0,
            "previous_grade": 45.0,
            "assignment_score": 40.0,
            "assessment_score": 42.0,
            "participation_score": 35.0,
            "sleep_hours": 5.0,
            "tutoring_sessions": 0,
            "extracurricular_activities": "No",
            "parental_education": "High School",
            "internet_access": "No"
        },
        "model_name": "Logistic Regression"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["risk_category"] in ["High Risk", "Moderate Risk"]
    # Check that attendance is marked as negative impact
    negative_factors = [f for f in res["contributing_factors"] if f["impact"] == "Negative"]
    assert len(negative_factors) > 0

def test_input_validation_error():
    # Invalid attendance > 100
    payload = {
        "student": {
            "student_id": "TEST_INVALID",
            "name": "Invalid Attendance",
            "attendance_percentage": 150.0,
            "study_hours_per_week": 10.0,
            "previous_grade": 70.0,
            "assignment_score": 70.0,
            "assessment_score": 70.0
        },
        "model_name": "XGBoost"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422  # Pydantic validation error

def test_llm_explanation_fallback():
    fallback = generate_grounded_fallback(
        student_name="Test Student",
        predicted_class="Low",
        risk_category="High Risk",
        risk_score=78.5,
        input_data={
            "attendance_percentage": 54.0,
            "study_hours_per_week": 5.0,
            "previous_grade": 48.0,
            "assignment_score": 50.0,
            "assessment_score": 45.0,
            "sleep_hours": 5.0
        },
        contributing_factors=[
            {"feature_name_clean": "Attendance Rate", "impact": "Negative", "value": "54%"}
        ]
    )
    assert "explanation" in fallback
    assert len(fallback["possible_causes"]) > 0
    assert len(fallback["attention_areas"]) > 0
    assert len(fallback["personalized_recommendations"]) > 0
    assert len(fallback["early_interventions"]) > 0

def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_students_in_db" in stats
    assert "model_accuracies" in stats
    assert "risk_distribution" in stats

def test_get_student_detail():
    response = client.get("/api/students?limit=5")
    assert response.status_code == 200
    students = response.json()["students"]
    if students:
        s_id = students[0]["student_id"]
        detail_resp = client.get(f"/api/student/{s_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["student"]["student_id"] == s_id

def test_best_model_prediction():
    payload = {
        "student": {
            "student_id": "TEST_BEST_001",
            "name": "Auto Best Model Student",
            "attendance_percentage": 88.0,
            "study_hours_per_week": 20.0,
            "previous_grade": 82.0,
            "assignment_score": 85.0,
            "assessment_score": 80.0,
            "participation_score": 80.0,
            "sleep_hours": 7.0,
            "tutoring_sessions": 1,
            "extracurricular_activities": "Yes",
            "parental_education": "Bachelor",
            "internet_access": "Yes"
        },
        "model_name": "Best Model"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["model_used"] in ["Logistic Regression", "Random Forest", "XGBoost"]
    assert res["predicted_class"] in ["High", "Medium", "Low", "Poor", "Average", "Good", "Excellent"]
    assert 0.0 <= res["confidence"] <= 1.0

def test_independent_training_and_comparison():
    response = client.post("/api/train")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "best_model" in data
    assert data["best_model"] in ["Logistic Regression", "Random Forest", "XGBoost"]
    assert data["best_training_accuracy"] > 0
    assert len(data["models_evaluated"]) == 3
    assert "Ensemble" not in data["models_evaluated"]
    assert "Ensemble (Voting)" not in data["models_evaluated"]
    
    # Verify comparison scores
    comparison = data["comparison"]
    assert len(comparison) == 3
    for comp in comparison:
        assert "model_name" in comp
        assert "train_accuracy" in comp
        assert "test_accuracy" in comp
        assert "f1_score" in comp
        assert "is_best" in comp
    # Best model must have the highest training accuracy
    best_item = [c for c in comparison if c["is_best"]][0]
    assert best_item["model_name"] == data["best_model"]
    for c in comparison:
        assert best_item["train_accuracy"] >= c["train_accuracy"]
