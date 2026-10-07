from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from backend.resume_analyzer.service import ResumeAnalyzerService
from backend.resume_analyzer.recruitment_analyzer import RecruitmentAnalyzer
from backend.services.db_service import DatabaseService

router = APIRouter(prefix="/api/resume", tags=["Resume Analyzer"])

@router.post("/analyze")
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
    student_id: Optional[str] = Form(None)
):
    """
    Upload and analyze student resume (PDF or DOCX).
    Extracts text, skills, education, projects, matches against recruitment dataset,
    and returns placement readiness and LLM gap analysis.
    """
    # Validate extension
    filename = file.filename or "resume"
    ext = filename.lower().split(".")[-1]
    if ext not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Only PDF (.pdf) and Word (.docx) files are supported."
        )

    # Read bytes
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty (0 bytes).")

    # Limit size (e.g., 10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 10MB.")

    result = await ResumeAnalyzerService.analyze_resume(
        file_source=content,
        filename=filename,
        student_id=student_id,
        save_to_db=True
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Analysis failed."))

    return result

@router.get("/recruitment-market")
async def get_recruitment_market_overview():
    """
    Get all recruitment companies, job roles, eligibility criteria, and empirical skill demand frequencies.
    """
    analyzer = RecruitmentAnalyzer()
    status = analyzer.get_status()
    if not status["available"]:
        return {
            "status": "warning",
            "message": status.get("error", "Recruitment dataset unavailable."),
            "companies": [],
            "frequencies": {}
        }

    records = analyzer.get_all_records()
    freqs = analyzer.calculate_skill_frequencies()
    return {
        "status": "success",
        "total_postings": len(records),
        "companies": records,
        "skill_frequencies": freqs
    }

@router.get("/history")
async def get_resume_history(limit: int = Query(10, ge=1, le=50)):
    """
    Get recent resume analyses stored in the system.
    """
    records = DatabaseService.get_recent_resume_analyses(limit=limit)
    return {"status": "success", "count": len(records), "analyses": records}

@router.get("/{analysis_id}")
async def get_resume_analysis_detail(analysis_id: int):
    """
    Get detailed results of a past resume analysis by ID.
    """
    analysis = DatabaseService.get_resume_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Resume analysis record not found.")
    return {"status": "success", "analysis": analysis}

@router.get("/student/{student_id}/profile")
async def get_student_combined_profile(student_id: str):
    """
    Connects student's academic profile, performance predictions, and resume analysis.
    """
    student = DatabaseService.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found.")

    predictions = DatabaseService.get_predictions_by_student(student_id)
    # Get latest resume analysis for this student if any
    all_resumes = DatabaseService.get_recent_resume_analyses(limit=50)
    matching_resume = next((r for r in all_resumes if r.get("student_id") == student_id), None)
    
    detailed_resume = None
    if matching_resume:
        detailed_resume = DatabaseService.get_resume_analysis_by_id(matching_resume["id"])

    return {
        "status": "success",
        "student": student,
        "latest_academic_prediction": predictions[0] if predictions else None,
        "total_predictions": len(predictions),
        "latest_resume_analysis": detailed_resume
    }
