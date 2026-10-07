import sqlite3
import json
from datetime import datetime
from backend.config import settings

def get_connection():
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        attendance_percentage REAL NOT NULL,
        study_hours_per_week REAL NOT NULL,
        previous_grade REAL NOT NULL,
        assignment_score REAL NOT NULL,
        assessment_score REAL NOT NULL,
        participation_score REAL DEFAULT 70.0,
        sleep_hours REAL DEFAULT 7.0,
        tutoring_sessions INTEGER DEFAULT 0,
        extracurricular_activities TEXT DEFAULT 'No',
        parental_education TEXT DEFAULT 'Bachelor',
        internet_access TEXT DEFAULT 'Yes',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Predictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        student_name TEXT,
        model_used TEXT NOT NULL,
        predicted_class TEXT NOT NULL,
        confidence REAL NOT NULL,
        risk_category TEXT NOT NULL,
        risk_score REAL NOT NULL,
        probabilities_json TEXT,
        contributions_json TEXT,
        input_data_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Model Metrics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        accuracy REAL NOT NULL,
        train_accuracy REAL DEFAULT 0.0,
        precision REAL NOT NULL,
        recall REAL NOT NULL,
        f1_score REAL NOT NULL,
        roc_auc REAL,
        confusion_matrix_json TEXT,
        feature_importance_json TEXT,
        trained_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migration: Ensure train_accuracy column exists if table already existed
    try:
        cursor.execute("ALTER TABLE model_metrics ADD COLUMN train_accuracy REAL DEFAULT 0.0;")
    except Exception:
        pass

    # Recommendations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        prediction_id INTEGER,
        explanation TEXT,
        possible_causes_json TEXT,
        attention_areas_json TEXT,
        recommendations_json TEXT,
        early_interventions_json TEXT,
        llm_model TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (prediction_id) REFERENCES predictions(id)
    );
    """)

    # Resume Analyses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        student_name TEXT,
        filename TEXT,
        extracted_info_json TEXT,
        matched_skills_json TEXT,
        partial_skills_json TEXT,
        missing_skills_json TEXT,
        readiness_score REAL DEFAULT 0.0,
        readiness_level TEXT,
        company_matches_json TEXT,
        llm_analysis_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", settings.DB_PATH)
