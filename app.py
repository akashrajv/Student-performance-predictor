# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import asyncio
from pathlib import Path

# Ensure paths
import sys
sys.path.insert(0, os.path.abspath("."))

from backend.config import settings
from backend.ml.predict import PredictionEngine
from backend.ml.train import train_all_models
from backend.llm.explanation import generate_llm_explanation, generate_grounded_fallback
from backend.services.db_service import DatabaseService
from backend.database.db import init_db
from backend.resume_analyzer.resume_ui import render_resume_analyzer_page

# Page config
st.set_page_config(
    page_title="Student Performance Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern Dark Blue & White theme
st.markdown("""
<style>
    /* White Background & Typography */
    .stApp, .main {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header & Badges */
    .hero-banner {
        background: linear-gradient(135deg, #091e42 0%, #1e3a8a 100%);
        border: 1px solid #1e40af;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25);
    }
    .hero-banner h2 {
        color: #ffffff !important;
    }
    .hero-banner p {
        color: #bfdbfe !important;
    }
    
    /* Metric Cards - White background with dark blue accent */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #1e3a8a;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.06);
    }
    .metric-card h4 {
        color: #1e3a8a !important;
    }
    .metric-card p {
        color: #475569 !important;
    }
    
    /* Sidebar Styling - Dark Blue */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a192f 0%, #0f2b5c 100%);
        border-right: 1px solid #1e3a8a;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #93c5fd !important;
    }
    
    /* Buttons - Dark Blue */
    .stButton>button {
        background-color: #1e3a8a;
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #172554;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
    }
    
    /* Badges */
    .badge-high-risk {
        background: rgba(244, 63, 94, 0.12);
        color: #e11d48;
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .badge-mod-risk {
        background: rgba(245, 158, 11, 0.12);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .badge-low-risk {
        background: rgba(16, 185, 129, 0.12);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .factor-negative {
        background: #fff1f2;
        border-left: 4px solid #f43f5e;
        color: #881337;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    
    .factor-positive {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        color: #064e3b;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    .report-card {
        background: #ffffff;
        border: 1px solid #bfdbfe;
        border-left: 5px solid #1e3a8a;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: 0 4px 15px -3px rgba(30, 58, 138, 0.08);
        color: #0f172a;
    }
    .report-card h4 {
        color: #1e3a8a !important;
    }
    .report-card p {
        color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Ensure models exist
if not (settings.ARTIFACTS_DIR / "xgboost.pkl").exists():
    with st.spinner("Training models for first-time setup..."):
        train_all_models()

# Sidebar
st.sidebar.markdown("""
<div style='text-align: center; padding-bottom: 12px;'>
    <h2 style='color: #818cf8; margin-bottom: 0;'>🎓 Performance Predictor</h2>
    <p style='font-size: 0.8rem; color: #94a3b8; margin-top: 4px;'>AI-Powered Academic Intelligence</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Executive Dashboard",
        "🎯 Predict Student Performance",
        "📁 Batch Cohort Prediction",
        "🔬 Model Analysis & Comparison",
        "👥 Student Directory & Profile",
        "📄 AI Resume Analyzer & Placement Readiness",
        "⚙️ Dataset & Model Retraining"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Project Details:**  
- **Author:** Akashraj (61782324110006)  
- **Architecture:** Multi-Model + Grounded LLM  
- **Models:** LR (L2), RF, XGBoost (Best Model Selected)  
""")

# ==============================================================================
# 1. EXECUTIVE DASHBOARD
# ==============================================================================
if menu == "📊 Executive Dashboard":
    st.markdown("""
    <div class='hero-banner'>
        <h1 style='color: white; margin: 0; font-size: 1.8rem;'>🎓 Student Performance Predictor Dashboard</h1>
        <p style='color: #94a3b8; margin-top: 6px; font-size: 0.95rem;'>
            Comparative multi-model machine learning architecture with Explainable AI (XAI) feature attribution and grounded LLM recommendations for early academic intervention.
        </p>
    </div>
    """, unsafe_allow_html=True)

    stats = DatabaseService.get_dashboard_statistics()
    metrics = PredictionEngine.get_metrics()

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students Enrolled", stats["total_students_in_db"], help="Total student records stored in SQLite database")
    with col2:
        st.metric("Students At High Risk", stats["high_risk_count"], delta=f"{stats['moderate_risk_count']} Moderate", delta_color="inverse")
    with col3:
        st.metric("Cohort Attendance Average", f"{stats['avg_attendance']}%", help="Mean attendance rate across cohort")
    with col4:
        st.metric("Average Risk Score", f"{stats['avg_predicted_risk']}%", help="Derived probability index of academic failure")

    st.markdown("<br>", unsafe_allow_html=True)


    # Recent Predictions
    st.subheader("Recent Prediction Log")
    if stats["recent_predictions"]:
        recent_df = pd.DataFrame(stats["recent_predictions"])
        st.dataframe(
            recent_df[["student_id", "student_name", "model_used", "predicted_class", "risk_category", "risk_score", "created_at"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No recent predictions recorded yet.")

# ==============================================================================
# 2. PREDICT STUDENT PERFORMANCE
# ==============================================================================
elif menu == "🎯 Predict Student Performance":
    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color: white; margin: 0;'>🎯 Predict Individual Student Performance</h2>
        <p style='color: #94a3b8; margin-top: 4px; font-size: 0.9rem;'>
            Input student metrics or load demo presets. Generates class predictions, risk categories, Explainable AI (XAI) feature attributions, and grounded LLM action plans.
        </p>
    </div>
    """, unsafe_allow_html=True)

    pipeline = PredictionEngine.get_pipeline()
    has_new_schema = "Previous_Semester_CGPA" in pipeline.numerical_cols

    # Demo Presets
    if has_new_schema:
        preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
        with preset_col1:
            if st.button("🚨 Load Poor / At-Risk Sample", use_container_width=True):
                st.session_state["p_id"] = "STU395"
                st.session_state["p_name"] = "Rohan Sharma"
                st.session_state["p_att"] = 58.4
                st.session_state["p_cgpa"] = 5.20
                st.session_state["p_internal"] = 31.0
                st.session_state["p_assign"] = 50.0
                st.session_state["p_quiz"] = 23.0
                st.session_state["p_study_day"] = 0.4
                st.session_state["p_backlogs"] = 3
                st.session_state["p_practical"] = 55.0
        with preset_col2:
            if st.button("⚖️ Load Average Sample", use_container_width=True):
                st.session_state["p_id"] = "STU362"
                st.session_state["p_name"] = "Kavya Patel"
                st.session_state["p_att"] = 79.0
                st.session_state["p_cgpa"] = 5.50
                st.session_state["p_internal"] = 53.0
                st.session_state["p_assign"] = 50.0
                st.session_state["p_quiz"] = 50.0
                st.session_state["p_study_day"] = 2.0
                st.session_state["p_backlogs"] = 1
                st.session_state["p_practical"] = 55.0
        with preset_col3:
            if st.button("📘 Load Good Sample", use_container_width=True):
                st.session_state["p_id"] = "STU156"
                st.session_state["p_name"] = "Arjun Verma"
                st.session_state["p_att"] = 81.7
                st.session_state["p_cgpa"] = 7.51
                st.session_state["p_internal"] = 81.0
                st.session_state["p_assign"] = 77.0
                st.session_state["p_quiz"] = 78.0
                st.session_state["p_study_day"] = 4.4
                st.session_state["p_backlogs"] = 0
                st.session_state["p_practical"] = 84.0
        with preset_col4:
            if st.button("🌟 Load Excellent Sample", use_container_width=True):
                st.session_state["p_id"] = "STU074"
                st.session_state["p_name"] = "Akashraj Sundaram"
                st.session_state["p_att"] = 90.5
                st.session_state["p_cgpa"] = 9.28
                st.session_state["p_internal"] = 92.0
                st.session_state["p_assign"] = 91.0
                st.session_state["p_quiz"] = 92.0
                st.session_state["p_study_day"] = 7.8
                st.session_state["p_backlogs"] = 0
                st.session_state["p_practical"] = 87.0
    else:
        preset_col1, preset_col2, preset_col3 = st.columns(3)
        with preset_col1:
            if st.button("🚨 Load At-Risk Student Sample", use_container_width=True):
                st.session_state["p_id"] = "STU-RISK-201"
                st.session_state["p_name"] = "Rohan Sharma"
                st.session_state["p_att"] = 52.0
                st.session_state["p_study"] = 5.0
                st.session_state["p_prev"] = 48.0
                st.session_state["p_assign"] = 45.0
                st.session_state["p_assess"] = 42.0
                st.session_state["p_part"] = 40.0
                st.session_state["p_sleep"] = 5.5
                st.session_state["p_tutor"] = 0
                st.session_state["p_extra"] = "No"
                st.session_state["p_parent"] = "High School"
                st.session_state["p_net"] = "No"
        with preset_col2:
            if st.button("⚖️ Load Average / Moderate Student Sample", use_container_width=True):
                st.session_state["p_id"] = "STU-AVG-305"
                st.session_state["p_name"] = "Kavya Patel"
                st.session_state["p_att"] = 77.0
                st.session_state["p_study"] = 16.0
                st.session_state["p_prev"] = 70.0
                st.session_state["p_assign"] = 68.0
                st.session_state["p_assess"] = 69.0
                st.session_state["p_part"] = 72.0
                st.session_state["p_sleep"] = 7.0
                st.session_state["p_tutor"] = 1
                st.session_state["p_extra"] = "Yes"
                st.session_state["p_parent"] = "Bachelor"
                st.session_state["p_net"] = "Yes"
        with preset_col3:
            if st.button("🌟 Load High Distinction Student Sample", use_container_width=True):
                st.session_state["p_id"] = "STU-TOP-409"
                st.session_state["p_name"] = "Akashraj Sundaram"
                st.session_state["p_att"] = 96.0
                st.session_state["p_study"] = 28.0
                st.session_state["p_prev"] = 92.0
                st.session_state["p_assign"] = 94.0
                st.session_state["p_assess"] = 90.0
                st.session_state["p_part"] = 88.0
                st.session_state["p_sleep"] = 7.5
                st.session_state["p_tutor"] = 3
                st.session_state["p_extra"] = "Yes"
                st.session_state["p_parent"] = "Master"
                st.session_state["p_net"] = "Yes"

    st.markdown("---")

    with st.form("predict_form"):
        fcol1, fcol2 = st.columns(2)

        if has_new_schema:
            with fcol1:
                st.subheader("Student Identification & Academics")
                student_id = st.text_input("Student ID", value=st.session_state.get("p_id", "STU1001"))
                student_name = st.text_input("Full Name", value=st.session_state.get("p_name", "Student Name"))
                att = st.slider("Classroom Attendance Rate (%)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_att", 80.0)), step=0.1)
                cgpa = st.slider("Previous Semester CGPA (0.0 - 10.0)", min_value=0.0, max_value=10.0, value=float(st.session_state.get("p_cgpa", 7.0)), step=0.01)
                study_day = st.slider("Daily Study Hours", min_value=0.0, max_value=15.0, value=float(st.session_state.get("p_study_day", 3.0)), step=0.1)

            with fcol2:
                st.subheader("Continuous Assessments & Performance")
                internal = st.slider("Internal Assessment Marks (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_internal", 70.0)), step=0.5)
                assign = st.slider("Assignment Score (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_assign", 70.0)), step=0.5)
                quiz = st.slider("Quiz Score (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_quiz", 70.0)), step=0.5)
                practical = st.slider("Practical Lab Marks (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_practical", 75.0)), step=0.5)
                backlogs = st.number_input("Previous Backlogs Count", min_value=0, max_value=20, value=int(st.session_state.get("p_backlogs", 0)))
        else:
            with fcol1:
                st.subheader("Student Identification & Core Academics")
                student_id = st.text_input("Student ID", value=st.session_state.get("p_id", "STU-1001"))
                student_name = st.text_input("Full Name", value=st.session_state.get("p_name", "Student Name"))
                att = st.slider("Classroom Attendance Rate (%)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_att", 75.0)), step=0.5)
                study = st.slider("Self-Study Hours / Week", min_value=0.0, max_value=60.0, value=float(st.session_state.get("p_study", 15.0)), step=0.5)
                prev = st.slider("Previous Academic Grade (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_prev", 70.0)), step=0.5)

            with fcol2:
                st.subheader("Continuous Assessments & Habits")
                assign = st.slider("Assignment Performance Score (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_assign", 70.0)), step=0.5)
                assess = st.slider("Midterm / Exam Assessment Score (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_assess", 70.0)), step=0.5)
                part = st.slider("Classroom Participation Score (0-100)", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_part", 70.0)), step=0.5)
                
                subcol1, subcol2 = st.columns(2)
                with subcol1:
                    sleep = st.number_input("Sleep Hours / Night", min_value=3.0, max_value=14.0, value=float(st.session_state.get("p_sleep", 7.0)), step=0.5)
                    extra = st.selectbox("Extracurricular Activities", ["Yes", "No"], index=0 if st.session_state.get("p_extra", "No") == "Yes" else 1)
                with subcol2:
                    tutor = st.number_input("Monthly Tutoring Sessions", min_value=0, max_value=20, value=int(st.session_state.get("p_tutor", 0)))
                    parent_ed = st.selectbox("Parental Education", ["High School", "Bachelor", "Master", "Doctorate"], index=1)
                
                net = st.selectbox("High-Speed Internet Access", ["Yes", "No"], index=0 if st.session_state.get("p_net", "Yes") == "Yes" else 1)

        best_info = PredictionEngine.get_best_model_info()
        best_name = best_info.get("best_model_name", "Logistic Regression")
        
        model_name = st.selectbox(
            "Select Machine Learning Architecture",
            ["Model Consensus (Multi-Model Agreement)", f"Best Model ({best_name} - Auto-selected)", "Logistic Regression", "Random Forest", "XGBoost"],
            help="Model Consensus evaluates all 3 models (Logistic Regression, Random Forest, XGBoost) and performs majority voting."
        )

        submitted = st.form_submit_button("🚀 Predict Performance", use_container_width=True)

    if submitted:
        if has_new_schema:
            student_payload = {
                "Student_ID": student_id,
                "student_id": student_id,
                "Name": student_name,
                "name": student_name,
                "Attendance_Percentage": att,
                "attendance_percentage": att,
                "Previous_Semester_CGPA": cgpa,
                "previous_semester_cgpa": cgpa,
                "Internal_Marks": internal,
                "internal_marks": internal,
                "Assignment_Score": assign,
                "assignment_score": assign,
                "Quiz_Score": quiz,
                "quiz_score": quiz,
                "Study_Hours_Per_Day": study_day,
                "study_hours_per_day": study_day,
                "Previous_Backlogs": backlogs,
                "previous_backlogs": backlogs,
                "Practical_Marks": practical,
                "practical_marks": practical
            }
        else:
            student_payload = {
                "student_id": student_id,
                "name": student_name,
                "attendance_percentage": att,
                "study_hours_per_week": study,
                "previous_grade": prev,
                "assignment_score": assign,
                "assessment_score": assess,
                "participation_score": part,
                "sleep_hours": sleep,
                "tutoring_sessions": tutor,
                "extracurricular_activities": extra,
                "parental_education": parent_ed,
                "internet_access": net
            }

        # 1. Run multi-model consensus across all 3 models (LR, RF, XGBoost)
        consensus_res = PredictionEngine.predict_consensus(student_payload)

        # 2. If user requested a specific individual model, evaluate that model while attaching consensus
        if "consensus" in model_name.lower():
            res = consensus_res
        else:
            res = PredictionEngine.predict_single(student_payload, model_name=model_name)
            res["consensus"] = consensus_res["consensus"]
        
        # Save to DB
        DatabaseService.save_or_update_student(student_payload)
        pred_id = DatabaseService.save_prediction({
            "student_id": res["student_id"],
            "student_name": res["student_name"],
            "model_used": res["model_used"],
            "predicted_class": res["predicted_class"],
            "confidence": res["confidence"],
            "risk_category": res["risk_category"],
            "risk_score": res["risk_score"],
            "probabilities": res["probabilities"],
            "contributing_factors": res["contributing_factors"],
            "input_data": res["input_data"]
        })
        res["prediction_id"] = pred_id
        st.session_state["latest_prediction"] = res

    # Display Results if available
    if "latest_prediction" in st.session_state:
        pred = st.session_state["latest_prediction"]
        consensus = pred.get("consensus")

        # ==============================================================================
        # 🤖 MODEL CONSENSUS – Multi-Model Agreement Section
        # ==============================================================================
        if consensus:
            st.markdown("---")
            st.markdown("""
            <div style='background: linear-gradient(135deg, #091e42 0%, #0f2744 100%); border: 2px solid #2563eb; border-radius: 16px; padding: 22px 26px; margin-bottom: 22px; box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);'>
                <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.12); padding-bottom: 12px; margin-bottom: 16px;'>
                    <div style='display: flex; align-items: center; gap: 12px;'>
                        <span style='font-size: 1.8rem;'>🤖</span>
                        <div>
                            <h3 style='color: #ffffff; margin: 0; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.01em;'>MODEL CONSENSUS</h3>
                            <p style='color: #93c5fd; margin: 2px 0 0 0; font-size: 0.85rem;'>Multi-Model Agreement Layer (Logistic Regression, Random Forest, XGBoost)</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            mcol1, mcol2, mcol3 = st.columns(3)
            m_preds = consensus.get("model_predictions", {})

            with mcol1:
                lr_info = m_preds.get("Logistic Regression", {})
                lr_pred = lr_info.get("prediction", "Unknown")
                lr_conf = lr_info.get("confidence_display", "Confidence unavailable")
                badge_class = "badge-high-risk" if "High" in lr_pred else ("badge-mod-risk" if "Mod" in lr_pred else "badge-low-risk")
                st.markdown(f"""
                <div style='background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 16px; text-align: center;'>
                    <div style='font-weight: 700; color: #93c5fd; font-size: 0.95rem; margin-bottom: 8px;'>Logistic Regression</div>
                    <div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 4px;'>Prediction:</div>
                    <div style='margin-bottom: 8px;'><span class='{badge_class}'>{lr_pred}</span></div>
                    <div style='font-size: 0.8rem; color: #94a3b8;'>Confidence: <strong style='color: #f8fafc;'>{lr_conf}</strong></div>
                </div>
                """, unsafe_allow_html=True)

            with mcol2:
                rf_info = m_preds.get("Random Forest", {})
                rf_pred = rf_info.get("prediction", "Unknown")
                rf_conf = rf_info.get("confidence_display", "Confidence unavailable")
                badge_class = "badge-high-risk" if "High" in rf_pred else ("badge-mod-risk" if "Mod" in rf_pred else "badge-low-risk")
                st.markdown(f"""
                <div style='background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 16px; text-align: center;'>
                    <div style='font-weight: 700; color: #a78bfa; font-size: 0.95rem; margin-bottom: 8px;'>Random Forest</div>
                    <div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 4px;'>Prediction:</div>
                    <div style='margin-bottom: 8px;'><span class='{badge_class}'>{rf_pred}</span></div>
                    <div style='font-size: 0.8rem; color: #94a3b8;'>Confidence: <strong style='color: #f8fafc;'>{rf_conf}</strong></div>
                </div>
                """, unsafe_allow_html=True)

            with mcol3:
                xgb_info = m_preds.get("XGBoost", {})
                xgb_pred = xgb_info.get("prediction", "Unknown")
                xgb_conf = xgb_info.get("confidence_display", "Confidence unavailable")
                badge_class = "badge-high-risk" if "High" in xgb_pred else ("badge-mod-risk" if "Mod" in xgb_pred else "badge-low-risk")
                st.markdown(f"""
                <div style='background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 16px; text-align: center;'>
                    <div style='font-weight: 700; color: #38bdf8; font-size: 0.95rem; margin-bottom: 8px;'>XGBoost</div>
                    <div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 4px;'>Prediction:</div>
                    <div style='margin-bottom: 8px;'><span class='{badge_class}'>{xgb_pred}</span></div>
                    <div style='font-size: 0.8rem; color: #94a3b8;'>Confidence: <strong style='color: #f8fafc;'>{xgb_conf}</strong></div>
                </div>
                """, unsafe_allow_html=True)

            # Consensus Outcome Container
            final_p = consensus.get("final_prediction", "Unknown")
            agree_disp = consensus.get("models_agree_display", "N/A")
            pct_disp = f"{consensus.get('consensus_percentage', 0.0):.2f}%"
            status_text = consensus.get("consensus_status", "N/A")
            avg_conf_disp = consensus.get("average_confidence_display", "Confidence unavailable")

            if "Strong" in status_text:
                status_badge = "<span style='background: #065f46; color: #6ee7b7; border: 1px solid #10b981; padding: 6px 16px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem;'>🟢 Strong Model Consensus</span>"
            elif "Moderate" in status_text:
                status_badge = "<span style='background: #78350f; color: #fde68a; border: 1px solid #f59e0b; padding: 6px 16px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem;'>🟡 Moderate Model Consensus</span>"
            else:
                status_badge = "<span style='background: #881337; color: #fecdd3; border: 1px solid #f43f5e; padding: 6px 16px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem;'>🔴 Model Disagreement – Prediction Uncertain</span>"

            st.markdown(f"""
            <div style='background: #0f172a; border: 1px solid #334155; border-radius: 14px; padding: 20px; margin-top: 14px; margin-bottom: 12px;'>
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; align-items: center;'>
                    <div>
                        <div style='font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;'>Final Prediction</div>
                        <div style='font-size: 1.35rem; font-weight: 800; color: #ffffff; margin-top: 2px;'>{final_p.upper()}</div>
                    </div>
                    <div>
                        <div style='font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;'>Models Agree</div>
                        <div style='font-size: 1.35rem; font-weight: 800; color: #38bdf8; margin-top: 2px;'>{agree_disp}</div>
                    </div>
                    <div>
                        <div style='font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;'>Consensus</div>
                        <div style='font-size: 1.35rem; font-weight: 800; color: #a78bfa; margin-top: 2px;'>{pct_disp}</div>
                    </div>
                    <div>
                        <div style='font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;'>Average Model Confidence</div>
                        <div style='font-size: 1.35rem; font-weight: 800; color: #34d399; margin-top: 2px;'>{avg_conf_disp}</div>
                    </div>
                </div>
                <div style='margin-top: 16px; padding-top: 14px; border-top: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;'>
                    <div>
                        <span style='color: #94a3b8; font-size: 0.85rem; font-weight: 600;'>Status: </span>
                        {status_badge}
                    </div>
                    <div style='color: #64748b; font-size: 0.78rem; font-style: italic;'>
                        ⚠️ Note: Model consensus reflects agreement across independent algorithms (majority voting) and is distinct from classification accuracy. 100% consensus does not mean 100% accuracy.
                    </div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🔍 Prediction Results & Academic Risk Assessment")

        rcol1, rcol2, rcol3, rcol4 = st.columns(4)
        with rcol1:
            st.metric("Predicted Performance", pred["predicted_class"])
        with rcol2:
            st.metric("Model Confidence", f"{round(pred['confidence'] * 100, 1)}%", help=f"Evaluated by {pred['model_used']}")
        with rcol3:
            st.metric("Academic Risk Score", f"{pred['risk_score']}%", help="Derived failure probability")
        with rcol4:
            risk_cat = pred["risk_category"]
            if "High" in risk_cat:
                st.markdown(f"<div style='margin-top: 14px;'><span class='badge-high-risk'>🚨 {risk_cat}</span></div>", unsafe_allow_html=True)
            elif "Mod" in risk_cat:
                st.markdown(f"<div style='margin-top: 14px;'><span class='badge-mod-risk'>⚠️ {risk_cat}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='margin-top: 14px;'><span class='badge-low-risk'>✅ {risk_cat}</span></div>", unsafe_allow_html=True)

        # Probabilities
        st.markdown("**Class Probabilities:**")
        prob_df = pd.DataFrame([
            {"Performance Class": k, "Probability (%)": round(v * 100, 1)}
            for k, v in pred["probabilities"].items()
        ])
        fig_prob = px.bar(
            prob_df,
            x="Performance Class",
            y="Probability (%)",
            color="Performance Class",
            color_discrete_map={
                "Excellent": "#10b981", "Good": "#06b6d4", "Average": "#f59e0b", "Poor": "#f43f5e",
                "High": "#10b981", "Medium": "#f59e0b", "Low": "#f43f5e"
            },
            template="plotly_dark",
            text="Probability (%)"
        )
        fig_prob.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_prob, use_container_width=True)

        # Explainable AI Attribution
        st.subheader("📊 Explainable AI (XAI): Why is this student predicted this way?")
        st.caption("Quantifies individual feature attribution and deviation from cohort benchmarks.")

        factors = pred.get("contributing_factors", [])
        if factors:
            f_chart_data = []
            for f in factors:
                f_chart_data.append({
                    "Feature": f["feature_name_clean"],
                    "Contribution Score": f["contribution_score"],
                    "Impact": f["impact"]
                })
            df_fc = pd.DataFrame(f_chart_data)
            fig_fc = px.bar(
                df_fc,
                x="Contribution Score",
                y="Feature",
                orientation="h",
                color="Impact",
                color_discrete_map={"Negative": "#f43f5e", "Positive": "#10b981", "Neutral": "#94a3b8"},
                template="plotly_dark"
            )
            fig_fc.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_fc, use_container_width=True)

            # Factors list
            fcol_left, fcol_right = st.columns(2)
            neg_factors = [f for f in factors if f["impact"] == "Negative"]
            pos_factors = [f for f in factors if f["impact"] == "Positive"]

            with fcol_left:
                st.markdown("##### 🚨 Primary Risk Drivers")
                if neg_factors:
                    for nf in neg_factors[:4]:
                        st.markdown(f"""
                        <div class='factor-negative'>
                            <strong>{nf['feature_name_clean']}:</strong> {nf['value']} (Benchmark: {nf['benchmark']})<br>
                            <span style='font-size: 0.85rem; color: #cbd5e1;'>{nf['description']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No major risk factors detected.")

            with fcol_right:
                st.markdown("##### ✅ Protective Strengths")
                if pos_factors:
                    for pf in pos_factors[:4]:
                        st.markdown(f"""
                        <div class='factor-positive'>
                            <strong>{pf['feature_name_clean']}:</strong> {pf['value']} (Benchmark: {pf['benchmark']})<br>
                            <span style='font-size: 0.85rem; color: #cbd5e1;'>{pf['description']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No significant positive deviations detected.")

        # Grounded LLM Layer
        st.markdown("---")
        st.subheader("🤖 AI Academic Advisor & Personalized Action Plan")
        st.caption("Synthesizes ML outputs into structured, empathetic, and strictly data-grounded interventions.")

        if st.button("✨ Generate AI Explanation & Action Plan", use_container_width=True):
            with st.spinner("Generating grounded pedagogical report..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    expl = loop.run_until_complete(
                        generate_llm_explanation(
                            student_id=pred["student_id"],
                            student_name=pred["student_name"],
                            input_data=pred["input_data"],
                            predicted_class=pred["predicted_class"],
                            confidence=pred["confidence"],
                            risk_category=pred["risk_category"],
                            risk_score=pred["risk_score"],
                            contributing_factors=pred["contributing_factors"],
                            consensus=pred.get("consensus")
                        )
                    )
                    # Save recommendation to DB
                    DatabaseService.save_recommendation({
                        "student_id": pred["student_id"],
                        "prediction_id": pred["prediction_id"],
                        "explanation": expl.get("explanation", ""),
                        "possible_causes": expl.get("possible_causes", []),
                        "attention_areas": expl.get("attention_areas", []),
                        "personalized_recommendations": expl.get("personalized_recommendations", []),
                        "early_interventions": expl.get("early_interventions", []),
                        "model_used": expl.get("model_used", "AI Engine")
                    })
                    st.session_state["llm_report"] = expl
                except Exception as e:
                    st.error(f"Error generating LLM report: {e}")

        if "llm_report" in st.session_state:
            rep = st.session_state["llm_report"]
            st.markdown(f"""
            <div class='report-card'>
                <h4 style='color: #818cf8; margin-top: 0;'>📋 Executive Academic Summary</h4>
                <p style='color: #f1f5f9; line-height: 1.6;'>{rep.get('explanation')}</p>
            </div>
            """, unsafe_allow_html=True)

            rep_col1, rep_col2 = st.columns(2)
            with rep_col1:
                st.markdown("##### 🔍 Identified Causes of Underperformance")
                for c in rep.get("possible_causes", []):
                    st.markdown(f"- {c}")

                st.markdown("##### 🎯 Areas Requiring Immediate Attention")
                for a in rep.get("attention_areas", []):
                    st.markdown(f"- **{a}**")

            with rep_col2:
                st.markdown("##### 📚 Personalized Recommendations for Student")
                for idx, r in enumerate(rep.get("personalized_recommendations", []), 1):
                    st.markdown(f"{idx}. {r}")

                st.markdown("##### 👨‍🏫 Early Interventions for Educators")
                for idx, i in enumerate(rep.get("early_interventions", []), 1):
                    st.markdown(f"- {i}")

# ==============================================================================
# 3. BATCH COHORT PREDICTION
# ==============================================================================
elif menu == "📁 Batch Cohort Prediction":
    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color: white; margin: 0;'>📁 Batch Cohort Performance Prediction</h2>
        <p style='color: #94a3b8; margin-top: 4px; font-size: 0.9rem;'>
            Upload student cohort records in CSV format to batch evaluate academic risk and export structured reports.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Download Template Button
    if settings.SAMPLE_TEMPLATE_PATH.exists():
        with open(settings.SAMPLE_TEMPLATE_PATH, "rb") as f:
            st.download_button(
                label="📥 Download Sample CSV Upload Template",
                data=f,
                file_name="student_performance_sample_template.csv",
                mime="text/csv"
            )

    uploaded_file = st.file_uploader("Upload Student Cohort CSV File", type=["csv"])
    b_model = st.selectbox("Select Model for Batch Scoring", ["Model Consensus (Multi-Model Agreement)", "Best Model (Auto-selected)", "XGBoost", "Random Forest", "Logistic Regression"])

    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.markdown(f"**Previewing Uploaded Dataset ({len(df_upload)} students):**")
            st.dataframe(df_upload.head(6), use_container_width=True)

            if st.button("🚀 Run Batch Prediction on Entire Cohort", use_container_width=True):
                progress_bar = st.progress(0)
                predictions = []
                students_to_save = []
                is_consensus_mode = bool("consensus" in b_model.lower())

                for idx, row in df_upload.iterrows():
                    row_dict = row.to_dict()
                    if 'student_id' not in row_dict and 'Student_ID' not in row_dict:
                        row_dict['student_id'] = f"BATCH-{idx+1:04d}"
                    if 'name' not in row_dict and 'Name' not in row_dict:
                        row_dict['name'] = f"Student {idx+1}"

                    # Compute multi-model consensus for comprehensive agreement analysis
                    c_res = PredictionEngine.predict_consensus(row_dict)
                    if is_consensus_mode:
                        p_res = c_res
                    else:
                        p_res = PredictionEngine.predict_single(row_dict, model_name=b_model)
                        p_res["consensus"] = c_res["consensus"]

                    predictions.append(p_res)
                    students_to_save.append(row_dict)
                    progress_bar.progress((idx + 1) / len(df_upload))

                # Batch save
                DatabaseService.save_students_batch(students_to_save)
                st.session_state["batch_results"] = predictions
                st.success(f"Successfully scored {len(predictions)} students using {b_model}!")

        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    if "batch_results" in st.session_state:
        b_preds = st.session_state["batch_results"]
        st.markdown("---")
        st.subheader("📊 Batch Scoring Summary")

        # Risk distribution
        high_r = sum(1 for p in b_preds if p["risk_category"] == "High Risk")
        mod_r = sum(1 for p in b_preds if p["risk_category"] == "Moderate Risk")
        low_r = sum(1 for p in b_preds if p["risk_category"] == "Low Risk")

        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
        with bcol1:
            st.metric("Total Scored", len(b_preds))
        with bcol2:
            st.metric("🚨 High Risk", high_r)
        with bcol3:
            st.metric("⚠️ Moderate Risk", mod_r)
        with bcol4:
            st.metric("✅ Low Risk", low_r)

        # Table formatting with all Model Consensus columns
        table_rows = []
        for p in b_preds:
            c_data = p.get("consensus", {})
            m_preds = c_data.get("model_predictions", {})
            lr_pred = m_preds.get("Logistic Regression", {}).get("prediction", "N/A")
            rf_pred = m_preds.get("Random Forest", {}).get("prediction", "N/A")
            xgb_pred = m_preds.get("XGBoost", {}).get("prediction", "N/A")
            final_pred = c_data.get("final_prediction", p.get("risk_category", "N/A"))
            c_count = c_data.get("models_agree_display", f"{c_data.get('consensus_count', 0)} / 3")
            c_pct = f"{c_data.get('consensus_percentage', 0.0):.2f}%" if isinstance(c_data.get('consensus_percentage'), (int, float)) else str(c_data.get('consensus_percentage', 'N/A'))
            avg_conf = c_data.get("average_confidence_display", "Confidence unavailable")
            conf_str = f"{round(p['confidence'] * 100, 1)}%" if p.get('confidence') is not None else "Confidence unavailable"

            table_rows.append({
                "Student ID": p["student_id"],
                "Student Name": p["student_name"],
                "LR Prediction": lr_pred,
                "RF Prediction": rf_pred,
                "XGBoost Prediction": xgb_pred,
                "Final Prediction": final_pred,
                "Consensus Count": c_count,
                "Consensus Percentage": c_pct,
                "Average Confidence": avg_conf,
                "Risk Category": p.get("risk_category", "N/A"),
                "Risk Score (%)": p.get("risk_score", 0.0),
                "Model Confidence": conf_str,
                "Primary Risk Driver": p["contributing_factors"][0]["description"] if p.get("contributing_factors") else "N/A"
            })
        df_results = pd.DataFrame(table_rows)

        # Filter
        filter_risk = st.selectbox("Filter by Final Prediction", ["All", "High Risk", "Moderate Risk", "Low Risk", "Prediction Uncertain"])
        if filter_risk != "All":
            df_filtered = df_results[df_results["Final Prediction"] == filter_risk]
        else:
            df_filtered = df_results

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

        # Export CSV
        csv_data = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Scored Predictions CSV",
            data=csv_data,
            file_name=f"student_predictions_{b_model.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

# ==============================================================================
# 4. MODEL ANALYSIS & COMPARISON
# ==============================================================================
elif menu == "🔬 Model Analysis & Comparison":
    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color: white; margin: 0;'>🔬 Machine Learning Model Analysis</h2>
        <p style='color: #94a3b8; margin-top: 4px; font-size: 0.9rem;'>
            Independent training and evaluation of Logistic Regression (L2 Regularized), Random Forest, and XGBoost on student academic records.
        </p>
    </div>
    """, unsafe_allow_html=True)

    metrics = PredictionEngine.get_metrics()
    best_info = PredictionEngine.get_best_model_info()
    best_name = best_info.get("best_model_name", "XGBoost")
    best_train_acc = best_info.get("best_training_accuracy", 0)

    if not metrics:
        st.warning("No metrics found. Please train models first.")
    else:
        # Champion Model Banner
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #091e42 0%, #1e3a8a 100%); border: 1px solid #2563eb; border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(30, 58, 138, 0.2);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.5); padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;'>
                        ★ SELECTED CHAMPION MODEL
                    </span>
                    <h3 style='color: #ffffff; margin: 10px 0 4px 0;'>{best_name}</h3>
                    <p style='color: #bfdbfe; margin: 0; font-size: 0.85rem;'>
                        Achieved highest training accuracy ({round(best_train_acc * 100, 2)}%) among all independently trained architectures.
                    </p>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 0.75rem; color: #93c5fd;'>Training Accuracy</div>
                    <div style='font-size: 1.5rem; font-weight: 800; color: #34d399;'>{round(best_train_acc * 100, 2)}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Architecture cards (3 columns)
        col1, col2, col3 = st.columns(3)
        with col1:
            is_b1 = "Logistic Regression" == best_name
            st.markdown(f"""
            <div class='metric-card' style='border-color: {"#10b981" if is_b1 else "#e2e8f0"};'>
                <h4 style='color: #1e3a8a; margin-top: 0;'>Logistic Regression (L2) {"★" if is_b1 else ""}</h4>
                <p style='font-size: 0.8rem; color: #475569;'>
                    Simple & stable baseline. L2 (Ridge) penalty avoids collinear overfitting.
                </p>
                <div style='font-size: 0.8rem; color: #059669;'>Train Acc: <strong>{round(metrics.get("Logistic Regression", {}).get("train_accuracy", metrics.get("Logistic Regression", {}).get("accuracy", 0))*100, 2)}%</strong></div>
                <div style='font-size: 0.8rem; color: #1e40af;'>Test Acc: <strong>{round(metrics.get("Logistic Regression", {}).get("accuracy", 0)*100, 2)}%</strong></div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            is_b2 = "Random Forest" == best_name
            st.markdown(f"""
            <div class='metric-card' style='border-color: {"#10b981" if is_b2 else "#e2e8f0"};'>
                <h4 style='color: #1e3a8a; margin-top: 0;'>Random Forest {"★" if is_b2 else ""}</h4>
                <p style='font-size: 0.8rem; color: #475569;'>
                    100 de-correlated decision trees capturing complex nonlinear interactions.
                </p>
                <div style='font-size: 0.8rem; color: #059669;'>Train Acc: <strong>{round(metrics.get("Random Forest", {}).get("train_accuracy", metrics.get("Random Forest", {}).get("accuracy", 0))*100, 2)}%</strong></div>
                <div style='font-size: 0.8rem; color: #1e40af;'>Test Acc: <strong>{round(metrics.get("Random Forest", {}).get("accuracy", 0)*100, 2)}%</strong></div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            is_b3 = "XGBoost" == best_name
            st.markdown(f"""
            <div class='metric-card' style='border-color: {"#10b981" if is_b3 else "#e2e8f0"};'>
                <h4 style='color: #1e3a8a; margin-top: 0;'>XGBoost {"★" if is_b3 else ""}</h4>
                <p style='font-size: 0.8rem; color: #475569;'>
                    Gradient boosting minimizing loss residuals with second-order tree pruning.
                </p>
                <div style='font-size: 0.8rem; color: #059669;'>Train Acc: <strong>{round(metrics.get("XGBoost", {}).get("train_accuracy", metrics.get("XGBoost", {}).get("accuracy", 0))*100, 2)}%</strong></div>
                <div style='font-size: 0.8rem; color: #1e40af;'>Test Acc: <strong>{round(metrics.get("XGBoost", {}).get("accuracy", 0)*100, 2)}%</strong></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Comparative Table
        st.subheader("📋 Empirical Metrics & Accuracy Benchmark Comparison")
        table_metrics = []
        for m_name, m_data in metrics.items():
            if "ensemble" in m_name.lower():
                continue
            is_best = m_name == best_name
            table_metrics.append({
                "Model": m_name,
                "Training Accuracy (%)": round(m_data.get("train_accuracy", m_data["accuracy"]) * 100, 2),
                "Test Accuracy (%)": round(m_data["accuracy"] * 100, 2),
                "Precision (%)": round(m_data["precision"] * 100, 2),
                "Recall (%)": round(m_data["recall"] * 100, 2),
                "F1-Score (%)": round(m_data["f1_score"] * 100, 2),
                "ROC-AUC (OvR)": round(m_data["roc_auc"], 3) if m_data.get("roc_auc") else "N/A",
                "Status": "★ Best Model Selected" if is_best else "Candidate"
            })
        st.dataframe(pd.DataFrame(table_metrics), use_container_width=True, hide_index=True)

        # Interactive Confusion Matrix & Feature Importance
        m_col1, m_col2 = st.columns(2)

        with m_col1:
            st.subheader("Confusion Matrix")
            sel_m = st.selectbox("Select Model for Matrix", list(metrics.keys()))
            cm = metrics[sel_m].get("confusion_matrix", [])
            classes = metrics[sel_m].get("classes", ["High", "Medium", "Low"])
            if cm:
                fig_cm = px.imshow(
                    cm,
                    x=classes,
                    y=classes,
                    color_continuous_scale="Blues",
                    labels=dict(x="Predicted Class", y="Actual Class", color="Count"),
                    text_auto=True,
                    template="plotly_white"
                )
                fig_cm.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_cm, use_container_width=True)

        with m_col2:
            st.subheader("Global Feature Importance")
            sel_imp_m = st.selectbox("Select Model for Importance", ["XGBoost", "Random Forest", "Logistic Regression"])
            importances = metrics.get(sel_imp_m, {}).get("feature_importance", {})
            if importances:
                imp_df = pd.DataFrame([
                    {"Feature": k.replace("_", " "), "Importance (%)": round(v * 100, 2)}
                    for k, v in importances.items()
                ]).sort_values("Importance (%)", ascending=True)
                fig_imp = px.bar(
                    imp_df,
                    x="Importance (%)",
                    y="Feature",
                    orientation="h",
                    color="Importance (%)",
                    color_continuous_scale="Blues",
                    template="plotly_white"
                )
                fig_imp.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_imp, use_container_width=True)

# ==============================================================================
# 5. STUDENT DIRECTORY & PROFILE
# ==============================================================================
elif menu == "👥 Student Directory & Profile":
    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color: white; margin: 0;'>👥 Student Academic Directory & 360° Profile</h2>
        <p style='color: #94a3b8; margin-top: 4px; font-size: 0.9rem;'>
            Lookup student records, analyze comprehensive academic profiles, and review historical AI action plans.
        </p>
    </div>
    """, unsafe_allow_html=True)

    search_query = st.text_input("🔍 Search Student by ID or Name", "")
    students_list = DatabaseService.get_all_students(limit=50, search=search_query)

    if not students_list:
        st.info("No matching students found in database.")
    else:
        student_options = {f"{s['student_id']} - {s['name']}": s['student_id'] for s in students_list}
        selected_key = st.selectbox("Select Student Profile", list(student_options.keys()))
        selected_id = student_options[selected_key]

        data = DatabaseService.get_student_by_id(selected_id)
        if data:
            stu = data["student"]
            pred = data["latest_prediction"]
            rec = data["latest_recommendation"]

            st.markdown("---")
            p_col1, p_col2 = st.columns([2, 1])

            with p_col1:
                st.markdown(f"### {stu['name']} (`{stu['student_id']}`)")
                st.write(f"Parent Education: **{stu['parental_education']}** | Internet Access: **{stu['internet_access']}** | Extracurricular: **{stu['extracurricular_activities']}**")

            with p_col2:
                if pred:
                    rc = pred["risk_category"]
                    if "High" in rc:
                        st.markdown(f"<span class='badge-high-risk'>🚨 {rc}</span>", unsafe_allow_html=True)
                    elif "Mod" in rc:
                        st.markdown(f"<span class='badge-mod-risk'>⚠️ {rc}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span class='badge-low-risk'>✅ {rc}</span>", unsafe_allow_html=True)

            # Metrics
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Attendance", f"{stu['attendance_percentage']}%")
            sc2.metric("Study Hours", f"{stu['study_hours_per_week']}h/wk")
            sc3.metric("Previous Grade", f"{stu['previous_grade']}/100")
            sc4.metric("Assessment Score", f"{stu['assessment_score']}/100")

            if pred:
                st.markdown("#### Latest Prediction Details")
                st.write(f"Model: **{pred['model_used']}** | Predicted Class: **{pred['predicted_class']}** | Confidence: **{round(pred['confidence']*100, 1)}%** | Risk Score: **{pred['risk_score']}%**")

            if rec:
                st.markdown("""
                <div class='report-card'>
                    <h4 style='color: #818cf8; margin-top: 0;'>📋 Stored AI Recommendation Plan</h4>
                    <p style='color: #f1f5f9;'>""" + rec.get("explanation", "") + """</p>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# 6. DATASET & MODEL RETRAINING
# ==============================================================================
elif menu == "⚙️ Dataset & Model Retraining":
    st.markdown("""
    <div class='hero-banner'>
        <h2 style='color: white; margin: 0;'>⚙️ Dataset Management & Model Retraining</h2>
        <p style='color: #94a3b8; margin-top: 4px; font-size: 0.9rem;'>
            Inspect training records, upload custom datasets, and trigger automated independent retraining of Logistic Regression (L2), Random Forest, and XGBoost.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if settings.RAW_DATA_PATH.exists():
        df_raw = pd.read_csv(settings.RAW_DATA_PATH)
        st.markdown(f"**Current Dataset Size:** `{len(df_raw)} records` | **Features:** `{len(df_raw.columns)} columns`")
        
        st.subheader("Dataset Sample (First 10 records)")
        st.dataframe(df_raw.head(10), use_container_width=True)

        target_col = None
        for cand in ['Performance_Level', 'Performance_Class', 'Target', 'Label']:
            if cand in df_raw.columns:
                target_col = cand
                break
        if not target_col and len(df_raw.columns) > 0:
            target_col = df_raw.columns[-1]

        st.subheader(f"Target Class Distribution ({target_col})" if target_col else "Target Class Distribution")
        if target_col and target_col in df_raw.columns:
            st.write(df_raw[target_col].value_counts())

    st.markdown("---")
    st.subheader("Retrain All 3 Models Independently")
    st.caption("Re-executes independent training for Logistic Regression (L2), Random Forest, and XGBoost, benchmarks training accuracies, and automatically selects the highest-scoring model.")

    if st.button("🔄 Retrain All 3 Models Now", use_container_width=True):
        with st.spinner("Independently retraining Logistic Regression (L2), Random Forest, and XGBoost..."):
            res = train_all_models()
            PredictionEngine.reload_artifacts()
            st.success(f"All 3 models retrained independently! Best model chosen: {res['best_model']} (Train Accuracy: {round(res['best_training_accuracy']*100, 2)}%)")
            
            st.markdown("#### Model Accuracy Scores & Selection")
            if "comparison" in res:
                comp_df = pd.DataFrame(res["comparison"])
                st.dataframe(comp_df, use_container_width=True, hide_index=True)

# ==============================================================================
# 7. AI RESUME ANALYZER & PLACEMENT READINESS
# ==============================================================================
elif menu == "📄 AI Resume Analyzer & Placement Readiness":
    render_resume_analyzer_page()
