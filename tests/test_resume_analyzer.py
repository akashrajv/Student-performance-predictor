import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import io
import pytest
import docx
import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app
from backend.resume_analyzer.resume_parser import (
    extract_resume_text,
    extract_text_from_pdf,
    extract_text_from_docx
)
from backend.resume_analyzer.skill_extractor import extract_resume_information
from backend.resume_analyzer.recruitment_analyzer import RecruitmentAnalyzer
from backend.resume_analyzer.skill_matcher import SkillMatcher
from backend.resume_analyzer.placement_readiness import PlacementReadinessEngine
from backend.resume_analyzer.llm_resume_analyzer import generate_grounded_resume_fallback
from backend.resume_analyzer.service import ResumeAnalyzerService
from backend.ml.predict import PredictionEngine

client = TestClient(app)

def create_valid_test_docx() -> bytes:
    doc = docx.Document()
    doc.add_paragraph("Akashraj Sundaram\nEmail: akashraj@example.com | Phone: +91 9876543210")
    doc.add_paragraph("Bachelor of Technology in Computer Science and Engineering\nABC Institute | CGPA: 8.85 / 10")
    doc.add_paragraph("Technical Skills:\nPython, Java, C++, SQL, React, Node.js, Spring Boot, Docker, AWS, Git, Data Structures, Algorithms")
    doc.add_paragraph("Projects:\nMicroservices E-Commerce Platform using Docker, Spring Boot, and PostgreSQL. Reduced latency by 45%.")
    doc.add_paragraph("Experience:\nSoftware Engineer Intern at TechCorp.")
    doc.add_paragraph("Certifications:\nAWS Certified Cloud Practitioner")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

def create_valid_test_pdf() -> bytes:
    content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 195 >>
stream
BT
/F1 12 Tf
50 720 Td
(Akashraj Sundaram - Software Engineer - akashraj@example.com) Tj
0 -20 Td
(B.Tech Computer Science CGPA: 8.5) Tj
0 -20 Td
(Technical Skills: Python, Java, SQL, React, Node.js, Docker, AWS, Git, Data Structures, Algorithms) Tj
ET
endstream
endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000489 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
560
%%EOF"""
    return content

# ==============================================================================
# TEST 1: Upload a valid PDF resume
# ==============================================================================
def test_1_upload_valid_pdf_resume():
    pdf_bytes = create_valid_test_pdf()
    res = extract_resume_text(pdf_bytes, filename="candidate_resume.pdf")
    assert res["status"] == "success"
    assert "Akashraj" in res["text"] or "Python" in res["text"]
    assert len(res["text"]) >= 50

    # Test through FastAPI endpoint
    response = client.post(
        "/api/resume/analyze",
        files={"file": ("candidate_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "candidate_name" in data

# ==============================================================================
# TEST 2: Upload a valid DOCX resume
# ==============================================================================
def test_2_upload_valid_docx_resume():
    docx_bytes = create_valid_test_docx()
    res = extract_resume_text(docx_bytes, filename="candidate_resume.docx")
    assert res["status"] == "success"
    assert "Akashraj" in res["text"]
    assert "Spring Boot" in res["text"]

    # Test through FastAPI endpoint
    response = client.post(
        "/api/resume/analyze",
        files={"file": ("candidate_resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["education"]["degree"] == "B.Tech"

# ==============================================================================
# TEST 3: Resume containing many matching skills
# ==============================================================================
def test_3_resume_containing_many_matching_skills():
    target_skills = ["Python", "Java", "SQL", "React", "Docker", "AWS", "Git"]
    cand_skills = ["Python", "Java", "SQL", "React", "Docker", "AWS", "Git", "C++"]
    match_res = SkillMatcher.match_resume_against_skills(cand_skills, target_skills)
    
    assert len(match_res["matched_skills"]) >= 6
    assert len(match_res["missing_skills"]) <= 1
    assert match_res["match_score"] >= 85.0

# ==============================================================================
# TEST 4: Resume containing several missing skills
# ==============================================================================
def test_4_resume_containing_several_missing_skills():
    target_skills = ["Python", "Java", "SQL", "React", "Docker", "AWS", "Kubernetes", "Spring Boot"]
    cand_skills = ["HTML", "CSS", "Basic C"]
    match_res = SkillMatcher.match_resume_against_skills(cand_skills, target_skills)
    
    assert len(match_res["missing_skills"]) >= 6
    assert match_res["match_score"] < 30.0

# ==============================================================================
# TEST 5: Company-wise matching
# ==============================================================================
def test_5_company_wise_matching():
    analyzer = RecruitmentAnalyzer()
    records = analyzer.get_all_records()
    assert len(records) > 0, "Recruitment dataset must contain records"

    cand_skills = ["Python", "SQL", "Pandas", "Scikit-learn", "Machine Learning"]
    comp_matches = PlacementReadinessEngine.evaluate_all_companies(
        candidate_skills=cand_skills,
        candidate_cgpa=8.0,
        candidate_projects=[{"title": "ML Churn"}],
        company_records=records
    )

    assert len(comp_matches) == len(records)
    # Check that keys exist
    first = comp_matches[0]
    assert "company" in first
    assert "role" in first
    assert "alignment" in first
    assert "matched_skills" in first
    assert "missing_skills" in first
    assert first["alignment"] in ["High Alignment", "Moderate Alignment", "Low Alignment"]

# ==============================================================================
# TEST 6: Skill priority calculation
# ==============================================================================
def test_6_skill_priority_calculation():
    analyzer = RecruitmentAnalyzer()
    freqs = analyzer.calculate_skill_frequencies()

    assert freqs["total_companies"] > 0
    assert "frequency_counts" in freqs
    assert "priority_tiers" in freqs
    tiers = freqs["priority_tiers"]
    assert "High Priority" in tiers
    assert "Medium Priority" in tiers
    assert "Low Priority" in tiers

    # High priority skills should have count > 0
    if tiers["High Priority"]:
        assert tiers["High Priority"][0]["count"] >= 1
        assert tiers["High Priority"][0]["percentage"] >= 30.0

# ==============================================================================
# TEST 7: LLM recommendations
# ==============================================================================
def test_7_llm_recommendations():
    fallback = generate_grounded_resume_fallback(
        candidate_name="Akashraj Sundaram",
        education_info={"degree": "B.Tech", "branch": "CSE", "cgpa": "8.5", "college": "ABC"},
        skills_data={"all_skills": ["Python", "SQL"]},
        matched_skills=["Python", "SQL"],
        partial_skills=["Machine Learning"],
        missing_skills=["Docker", "AWS", "Java"],
        priority_missing={"High Priority": [{"skill": "Docker", "frequency_count": 8, "frequency_percentage": 35.0}]},
        top_company_matches=[{"company": "Amazon", "role": "SDE", "alignment": "Moderate Alignment", "missing_skills": ["Java", "AWS"]}],
        projects=[{"title": "Student Predictor", "technologies": ["Python"]}],
        readiness_data={"readiness_score": 68.0, "readiness_level": "Promising Candidate"}
    )

    assert "resume_summary" in fallback
    assert "main_strengths" in fallback
    assert len(fallback["main_strengths"]) > 0
    assert "important_skill_gaps" in fallback
    assert "high_priority_skills_to_learn" in fallback
    assert "project_improvement_suggestions" in fallback
    assert "short_term_improvement_plan" in fallback

# ==============================================================================
# TEST 8: Invalid file upload
# ==============================================================================
def test_8_invalid_file_upload():
    # Unsupported extension
    res = extract_resume_text(b"Hello world this is a test text file", filename="resume.txt")
    assert res["status"] == "error"
    assert "Unsupported file format" in res["message"]

    # Invalid corrupted PDF bytes
    corrupt_res = extract_text_from_pdf(b"Not a real pdf at all just random garbage text")
    assert corrupt_res["status"] == "error"

# ==============================================================================
# TEST 9: Empty resume
# ==============================================================================
def test_9_empty_resume():
    empty_res = extract_resume_text(b"", filename="empty.pdf")
    assert empty_res["status"] == "error"
    assert "empty" in empty_res["message"].lower() or "0 bytes" in empty_res["message"].lower()

# ==============================================================================
# TEST 10: Missing recruitment dataset
# ==============================================================================
def test_10_missing_recruitment_dataset():
    analyzer = RecruitmentAnalyzer(dataset_path=Path("non_existent_recruitment_file_12345.csv"))
    status = analyzer.get_status()
    assert status["available"] is False
    assert status["error"] is not None
    assert "not found" in status["error"].lower()

    # Engine handles missing dataset gracefully
    records = analyzer.get_all_records()
    assert records == []

# ==============================================================================
# TEST 11: LLM/API failure fallback
# ==============================================================================
def test_11_llm_api_failure_fallback():
    # Test grounded fallback produces complete valid JSON
    fallback = generate_grounded_resume_fallback(
        candidate_name="Test Student",
        education_info={"degree": "B.Tech", "branch": "IT"},
        skills_data={"all_skills": ["C", "HTML"]},
        matched_skills=["C"],
        partial_skills=[],
        missing_skills=["Python", "SQL"],
        priority_missing={"High Priority": [{"skill": "SQL", "frequency_count": 10, "frequency_percentage": 40.0}]},
        top_company_matches=[],
        projects=[],
        readiness_data={"readiness_score": 35.0, "readiness_level": "Early Stage"}
    )
    assert fallback["model_used"] == "Grounded-Resume-Engine (Deterministic Ground Truth)"
    assert len(fallback["short_term_improvement_plan"]) >= 2

# ==============================================================================
# TEST 12: Verify that existing Student Performance Predictor still works
# ==============================================================================
def test_12_existing_student_performance_predictor_works():
    pred_payload = {
        "student": {
            "student_id": "TEST-STU-999",
            "name": "Integration Student",
            "attendance_percentage": 85.0,
            "study_hours_per_week": 18.0,
            "previous_grade": 75.0,
            "assignment_score": 78.0,
            "assessment_score": 80.0,
            "participation_score": 75.0,
            "sleep_hours": 7.0,
            "tutoring_sessions": 1,
            "extracurricular_activities": "Yes",
            "parental_education": "Bachelor",
            "internet_access": "Yes"
        },
        "model_name": "XGBoost"
    }
    response = client.post("/api/predict", json=pred_payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "risk_category" in data
    assert "contributing_factors" in data

# ==============================================================================
# TEST 13: Verify that Model Consensus still works
# ==============================================================================
def test_13_model_consensus_still_works():
    pred_payload = {
        "student": {
            "student_id": "TEST-STU-999",
            "name": "Integration Student",
            "attendance_percentage": 92.0,
            "study_hours_per_week": 25.0,
            "previous_grade": 88.0,
            "assignment_score": 90.0,
            "assessment_score": 86.0,
            "participation_score": 85.0,
            "sleep_hours": 7.5,
            "tutoring_sessions": 2,
            "extracurricular_activities": "Yes",
            "parental_education": "Master",
            "internet_access": "Yes"
        },
        "model_name": "Model Consensus"
    }
    response = client.post("/api/predict-consensus", json=pred_payload)
    assert response.status_code == 200
    data = response.json()
    assert "consensus" in data
    assert data["consensus"]["total_models"] == 3
    assert data["consensus"]["consensus_percentage"] in [66.7, 100.0]

# ==============================================================================
# TEST 14: Verify that Explainable AI still works
# ==============================================================================
def test_14_explainable_ai_still_works():
    pred_payload = {
        "student": {
            "student_id": "TEST-STU-999",
            "name": "Integration Student",
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
        "model_name": "XGBoost"
    }
    response = client.post("/api/predict", json=pred_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["contributing_factors"]) > 0
    # Factors have impact and direction
    first_factor = data["contributing_factors"][0]
    assert ("feature" in first_factor or "feature_name_clean" in first_factor)
    assert "impact" in first_factor
    assert ("description" in first_factor or "value" in first_factor)
