from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class StudentInput(BaseModel):
    student_id: str = Field(..., description="Unique student identifier (e.g. STU1001)")
    name: Optional[str] = Field("Student", description="Student full name")
    attendance_percentage: float = Field(..., ge=0, le=100, description="Attendance percentage (0-100)")
    assignment_score: float = Field(..., ge=0, le=100, description="Continuous assignment average (0-100)")
    # New dataset fields
    previous_semester_cgpa: Optional[float] = Field(None, ge=0, le=10, description="Previous Semester CGPA (0.0 - 10.0)")
    internal_marks: Optional[float] = Field(None, ge=0, le=100, description="Internal Marks (0-100)")
    quiz_score: Optional[float] = Field(None, ge=0, le=100, description="Quiz Score (0-100)")
    study_hours_per_day: Optional[float] = Field(None, ge=0, le=24, description="Daily self-study hours")
    previous_backlogs: Optional[int] = Field(None, ge=0, le=20, description="Number of previous backlogs")
    practical_marks: Optional[float] = Field(None, ge=0, le=100, description="Practical Lab Marks (0-100)")
    # Legacy fields
    study_hours_per_week: Optional[float] = Field(15.0, ge=0, le=80, description="Weekly self-study hours")
    previous_grade: Optional[float] = Field(70.0, ge=0, le=100, description="Previous academic score or scaled grade (0-100)")
    assessment_score: Optional[float] = Field(70.0, ge=0, le=100, description="Midterm or test assessment score (0-100)")
    participation_score: Optional[float] = Field(70.0, ge=0, le=100, description="Class participation score (0-100)")
    sleep_hours: Optional[float] = Field(7.0, ge=0, le=24, description="Average nightly sleep hours")
    tutoring_sessions: Optional[int] = Field(0, ge=0, le=20, description="Tutoring sessions attended per month")
    extracurricular_activities: Optional[str] = Field("No", description="'Yes' or 'No'")
    parental_education: Optional[str] = Field("Bachelor", description="'High School', 'Bachelor', 'Master', 'Doctorate'")
    internet_access: Optional[str] = Field("Yes", description="'Yes' or 'No'")

class PredictRequest(BaseModel):
    student: StudentInput
    model_name: Optional[str] = Field("Best Model", description="'Best Model', 'Model Consensus', 'Logistic Regression', 'Random Forest', or 'XGBoost'")

class FactorContribution(BaseModel):
    feature: str
    feature_name_clean: str
    value: Any
    impact: str  # "Positive", "Negative", "Neutral"
    contribution_score: float
    description: str

class PredictResponse(BaseModel):
    student_id: str
    student_name: str
    model_used: str
    predicted_class: str  # "High", "Medium", "Low", "Poor", "Average", "Good", "Excellent"
    confidence: Optional[float] = None  # 0.0 - 1.0 or None if unavailable
    risk_category: str  # "Low Risk", "Moderate Risk", "High Risk"
    risk_score: float  # 0.0 - 100.0%
    probabilities: Dict[str, float]
    contributing_factors: List[FactorContribution]
    prediction_id: Optional[int] = None
    created_at: Optional[str] = None
    consensus: Optional[Dict[str, Any]] = None

class BatchPredictResponse(BaseModel):
    total_students: int
    model_used: str
    risk_distribution: Dict[str, int]
    performance_distribution: Dict[str, int]
    predictions: List[PredictResponse]

class LLMExplainRequest(BaseModel):
    student_id: str
    student_name: str
    input_data: Dict[str, Any]
    predicted_class: str
    confidence: Optional[float] = None
    risk_category: str
    risk_score: float
    contributing_factors: List[FactorContribution]
    prediction_id: Optional[int] = None
    consensus: Optional[Dict[str, Any]] = None

class LLMExplainResponse(BaseModel):
    student_id: str
    student_name: str
    predicted_class: str
    risk_category: str
    explanation: str
    possible_causes: List[str]
    attention_areas: List[str]
    personalized_recommendations: List[str]
    early_interventions: List[str]
    model_used: str
    saved_to_db: bool = False

class TrainRequest(BaseModel):
    target_column: Optional[str] = "Performance_Class"

class TrainResponse(BaseModel):
    status: str
    message: str
    dataset_records: int
    train_size: int
    test_size: int
    models_evaluated: List[str]
    best_model: Optional[str] = None
    best_training_accuracy: Optional[float] = None
    comparison: Optional[List[Dict[str, Any]]] = None
    metrics: Dict[str, Any]
    trained_at: str

class DashboardStatsResponse(BaseModel):
    total_students_in_db: int
    total_predictions: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    avg_attendance: float
    avg_predicted_risk: float
    best_model: Optional[str] = None
    model_accuracies: Dict[str, float]
    risk_distribution: Dict[str, int]
    recent_predictions: List[Dict[str, Any]]
