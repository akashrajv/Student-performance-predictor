import sys
from pathlib import Path
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app
from backend.ml.consensus import (
    calculate_model_consensus,
    calculate_average_confidence,
    generate_consensus_summary,
    predict_with_all_models,
    predict_consensus
)
from backend.ml.predict import PredictionEngine
from backend.llm.explanation import generate_grounded_fallback

client = TestClient(app)


# ==============================================================================
# SPECIFICATION REQUIRED TEST CASES (CASES 1, 2, 3)
# ==============================================================================

def test_case_1_all_three_models_agree_high_risk():
    """
    CASE 1:
    All 3 models predict High Risk.
    Expected:
      3/3
      100%
      Strong Model Consensus
    """
    predictions = {
        "Logistic Regression": {"prediction": "High Risk", "confidence": 0.85},
        "Random Forest": {"prediction": "High Risk", "confidence": 0.88},
        "XGBoost": {"prediction": "High Risk", "confidence": 0.90}
    }

    consensus = calculate_model_consensus(predictions)

    assert consensus["consensus_count"] == 3
    assert consensus["total_models"] == 3
    assert consensus["models_agree_display"] == "3 / 3"
    assert consensus["consensus_percentage"] == 100.0
    assert consensus["consensus_status"] == "Strong Model Consensus"
    assert consensus["final_prediction"] == "High Risk"
    assert len(consensus["agreeing_models"]) == 3
    assert len(consensus["disagreeing_models"]) == 0


def test_case_2_two_models_agree_moderate_consensus():
    """
    CASE 2:
    2 models predict High Risk and 1 predicts Low Risk.
    Expected:
      2/3
      66.67%
      Moderate Model Consensus
      Final = High Risk
    """
    predictions = {
        "Logistic Regression": {"prediction": "High Risk", "confidence": 0.76},
        "Random Forest": {"prediction": "High Risk", "confidence": 0.81},
        "XGBoost": {"prediction": "Low Risk", "confidence": 0.64}
    }

    consensus = calculate_model_consensus(predictions)

    assert consensus["consensus_count"] == 2
    assert consensus["total_models"] == 3
    assert consensus["models_agree_display"] == "2 / 3"
    assert consensus["consensus_percentage"] == 66.67
    assert consensus["consensus_status"] == "Moderate Model Consensus"
    assert consensus["final_prediction"] == "High Risk"
    assert "Logistic Regression" in consensus["agreeing_models"]
    assert "Random Forest" in consensus["agreeing_models"]
    assert consensus["disagreeing_models"] == ["XGBoost"]


def test_case_3_all_three_models_disagree():
    """
    CASE 3:
    All 3 models predict different classes.
    Expected:
      Model Disagreement – Prediction Uncertain
    """
    predictions = {
        "Logistic Regression": {"prediction": "High Risk", "confidence": 0.55},
        "Random Forest": {"prediction": "Moderate Risk", "confidence": 0.60},
        "XGBoost": {"prediction": "Low Risk", "confidence": 0.58}
    }

    consensus = calculate_model_consensus(predictions)

    assert consensus["consensus_status"] == "Model Disagreement – Prediction Uncertain"
    assert consensus["final_prediction"] == "Prediction Uncertain"
    assert consensus["consensus_count"] == 1
    assert consensus["consensus_percentage"] == 33.33
    assert consensus["models_agree_display"] == "1 / 3"


# ==============================================================================
# CONFIDENCE CALCULATION TESTS
# ==============================================================================

def test_average_confidence_calculation():
    """
    If all models provide probabilities, calculate:
    average_confidence = (LR confidence + RF confidence + XGBoost confidence) / 3
    """
    # Example: 76%, 81%, 64% -> 73.67%
    confidences = [0.76, 0.81, 0.64]
    avg = calculate_average_confidence(confidences)
    assert avg is not None
    assert round(avg, 4) == round((0.76 + 0.81 + 0.64) / 3, 4)
    assert round(avg * 100, 1) == 73.7


def test_average_confidence_unavailable_when_missing():
    """
    If any model does not support probability prediction, confidence is unavailable.
    Do NOT invent confidence values.
    """
    # When one model has None confidence
    predictions = {
        "Logistic Regression": {"confidence": 0.80},
        "Random Forest": {"confidence": None},  # predict_proba unavailable
        "XGBoost": {"confidence": 0.85}
    }
    avg = calculate_average_confidence(predictions)
    assert avg is None


# ==============================================================================
# SUMMARY GENERATION TEST
# ==============================================================================

def test_generate_consensus_summary():
    consensus_data = {
        "final_prediction": "High Risk",
        "models_agree_display": "2 / 3",
        "consensus_percentage": 66.67,
        "consensus_status": "Moderate Model Consensus",
        "average_confidence_display": "73.7%",
        "model_predictions": {
            "Logistic Regression": {"prediction": "High Risk", "confidence_display": "76.0%"},
            "Random Forest": {"prediction": "High Risk", "confidence_display": "81.0%"},
            "XGBoost": {"prediction": "Moderate Risk", "confidence_display": "64.0%"}
        }
    }

    summary = generate_consensus_summary(consensus_data)
    assert "MODEL CONSENSUS" in summary
    assert "Logistic Regression" in summary
    assert "Random Forest" in summary
    assert "XGBoost" in summary
    assert "Final Prediction: HIGH RISK" in summary
    assert "Models Agree: 2 / 3" in summary
    assert "Consensus: 66.67%" in summary
    assert "Moderate Model Consensus" in summary
    assert "Average Model Confidence: 73.7%" in summary


# ==============================================================================
# PIPELINE INTEGRATION TESTS (REAL STUDENT DATA & MODELS)
# ==============================================================================

def test_predict_consensus_at_risk_student():
    student_payload = {
        "student_id": "TEST_CONSENSUS_RISK",
        "name": "At Risk Student",
        "attendance_percentage": 48.0,
        "study_hours_per_week": 5.0,
        "previous_grade": 45.0,
        "assignment_score": 42.0,
        "assessment_score": 40.0,
        "participation_score": 35.0,
        "sleep_hours": 5.0,
        "tutoring_sessions": 0,
        "extracurricular_activities": "No",
        "parental_education": "High School",
        "internet_access": "No"
    }

    result = PredictionEngine.predict_consensus(student_payload)

    assert "consensus" in result
    c = result["consensus"]
    assert c["total_models"] == 3
    assert c["consensus_status"] in ["Strong Model Consensus", "Moderate Model Consensus"]
    assert c["final_prediction"] in ["High Risk", "Moderate Risk"]
    assert "model_predictions" in c
    assert "Logistic Regression" in c["model_predictions"]
    assert "Random Forest" in c["model_predictions"]
    assert "XGBoost" in c["model_predictions"]
    assert c["average_confidence"] is not None
    assert 0.0 <= c["average_confidence"] <= 1.0


def test_predict_consensus_api_endpoint():
    payload = {
        "student": {
            "student_id": "TEST_API_CONSENSUS",
            "name": "High Performer Student",
            "attendance_percentage": 95.0,
            "study_hours_per_week": 26.0,
            "previous_grade": 92.0,
            "assignment_score": 94.0,
            "assessment_score": 91.0,
            "participation_score": 88.0,
            "sleep_hours": 7.5,
            "tutoring_sessions": 2,
            "extracurricular_activities": "Yes",
            "parental_education": "Master",
            "internet_access": "Yes"
        },
        "model_name": "Model Consensus"
    }

    # Test /api/predict with Model Consensus
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "consensus" in data
    assert data["consensus"] is not None
    assert data["consensus"]["total_models"] == 3
    assert data["consensus"]["final_prediction"] in ["Low Risk", "Moderate Risk", "High Risk"]

    # Test dedicated /api/predict-consensus endpoint
    response2 = client.post("/api/predict-consensus", json=payload)
    assert response2.status_code == 200
    data2 = response2.json()
    assert "consensus" in data2
    assert data2["consensus"] is not None


def test_llm_explanation_incorporates_model_consensus():
    student_payload = {
        "attendance_percentage": 50.0,
        "study_hours_per_week": 4.0,
        "previous_grade": 45.0,
        "assignment_score": 40.0,
        "assessment_score": 42.0,
        "sleep_hours": 5.0
    }
    contributing_factors = [
        {"feature_name_clean": "Class Attendance", "value": "50%", "benchmark": "80%", "impact": "Negative"},
        {"feature_name_clean": "Self-Study Hours", "value": "4 hrs", "benchmark": "16 hrs", "impact": "Negative"}
    ]
    consensus_info = {
        "consensus_count": 3,
        "total_models": 3,
        "consensus_percentage": 100.0,
        "consensus_status": "Strong Model Consensus",
        "final_prediction": "High Risk",
        "agreeing_models": ["Logistic Regression", "Random Forest", "XGBoost"],
        "disagreeing_models": [],
        "average_confidence_display": "88.5%",
        "model_predictions": {
            "Logistic Regression": {"prediction": "High Risk", "confidence_display": "87.0%"},
            "Random Forest": {"prediction": "High Risk", "confidence_display": "91.0%"},
            "XGBoost": {"prediction": "High Risk", "confidence_display": "87.5%"}
        }
    }

    report = generate_grounded_fallback(
        student_name="Test Student",
        predicted_class="Low",
        risk_category="High Risk",
        risk_score=78.0,
        input_data=student_payload,
        contributing_factors=contributing_factors,
        consensus=consensus_info
    )

    explanation = report["explanation"]
    assert "All three machine learning models" in explanation
    assert "high risk" in explanation.lower()
    assert "100% consensus" in explanation
    assert "88.5%" in explanation
    assert "Class Attendance" in explanation or "Self-Study Hours" in explanation
