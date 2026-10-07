import io
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd

from backend.resume_analyzer.resume_parser import extract_resume_text
from backend.resume_analyzer.skill_extractor import extract_resume_information
from backend.resume_analyzer.recruitment_analyzer import RecruitmentAnalyzer
from backend.resume_analyzer.skill_matcher import SkillMatcher
from backend.resume_analyzer.placement_readiness import PlacementReadinessEngine
from backend.resume_analyzer.llm_resume_analyzer import generate_llm_resume_analysis
from backend.resume_analyzer.personalized_plan import PersonalizedPlanBuilder
from backend.services.db_service import DatabaseService

class ResumeAnalyzerService:
    """
    Unified end-to-end service for AI Resume Analysis and Placement Readiness.
    """

    @classmethod
    async def analyze_resume(
        cls,
        file_source: Union[bytes, io.BytesIO, str, Path],
        filename: str = "",
        student_id: Optional[str] = None,
        recruitment_df: Optional[pd.DataFrame] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Complete end-to-end analysis pipeline:
        1. Resume Text Extraction (PDF/DOCX)
        2. Factual Information & Skill Extraction
        3. Recruitment Dataset Analysis & Empirical Frequencies
        4. Programmatic Skill Matching (Matched / Partial / Missing)
        5. Empirical Skill Prioritization (High / Medium / Low)
        6. Company-wise Alignment Analysis
        7. Project-defined Placement Readiness Scoring
        8. Grounded / LLM Gap Analysis (reusing existing LLM)
        9. Personalized Prioritized Improvement Plan
        10. Optional SQLite Database Persistence & Student Linking
        """
        # Step 1: Text extraction
        parse_res = extract_resume_text(file_source, filename)
        if parse_res.get("status") == "error":
            return {
                "status": "error",
                "stage": "text_extraction",
                "message": parse_res.get("message", "Failed to extract text from resume.")
            }

        resume_text = parse_res["text"]

        # Step 2: Information extraction
        info_res = extract_resume_information(resume_text, filename=filename)
        if info_res.get("status") == "error":
            return {
                "status": "error",
                "stage": "information_extraction",
                "message": info_res.get("message", "Failed to analyze resume information.")
            }

        candidate_name = info_res["personal"]["name"]
        education_info = info_res["education"]
        skills_data = {
            "all_skills": info_res["all_skills"],
            "categorized_skills": info_res["technical_skills"],
            "total_skills_count": info_res["total_skills_count"]
        }
        projects = info_res["projects"]
        experience = info_res["experience"]
        certifications = info_res["certifications"]
        quality_analysis = info_res["quality_analysis"]

        # Parse CGPA as float if available
        candidate_cgpa = None
        cgpa_str = education_info.get("cgpa", "")
        if cgpa_str and cgpa_str != "Not explicitly specified":
            try:
                # Remove % or /10
                clean_cgpa = cgpa_str.replace("%", "").split("/")[0].strip()
                val = float(clean_cgpa)
                if val > 10.0:  # Percentage to 10 scale approximation
                    candidate_cgpa = round(val / 10.0, 2)
                else:
                    candidate_cgpa = val
            except Exception:
                candidate_cgpa = None

        # Step 3: Recruitment dataset analysis
        rec_analyzer = RecruitmentAnalyzer(df_override=recruitment_df)
        rec_status = rec_analyzer.get_status()

        if not rec_status["available"]:
            # Dataset missing or corrupted - handle gracefully
            dataset_warning = rec_status.get("error", "Recruitment dataset not available.")
            company_records = []
            freq_data = {
                "total_companies": 0,
                "frequency_counts": {},
                "frequency_percentages": {},
                "priority_tiers": {"High Priority": [], "Medium Priority": [], "Low Priority": []}
            }
            all_target_skills = []
        else:
            dataset_warning = None
            company_records = rec_analyzer.get_all_records()
            freq_data = rec_analyzer.calculate_skill_frequencies()
            # Compile unique required skills across all companies
            all_target_skills = list(freq_data["frequency_counts"].keys())

        # Step 4: Programmatic Skill Matching
        if all_target_skills:
            match_res = SkillMatcher.match_resume_against_skills(
                resume_skills=info_res["all_skills"],
                target_skills=all_target_skills
            )
            matched_skills = match_res["matched_skills"]
            partial_skills = match_res["partial_skills"]
            missing_skills = match_res["missing_skills"]
        else:
            # Fallback if no dataset available
            matched_skills = info_res["all_skills"]
            partial_skills = []
            missing_skills = ["SQL", "Data Structures", "Docker", "AWS", "Git"]

        # Step 5: Skill Prioritization using empirical frequencies
        priority_missing = SkillMatcher.prioritize_missing_skills(
            missing_skills=missing_skills,
            frequency_data=freq_data
        )

        # Step 6: Company-wise Alignment
        company_matches = PlacementReadinessEngine.evaluate_all_companies(
            candidate_skills=info_res["all_skills"],
            candidate_cgpa=candidate_cgpa,
            candidate_projects=projects,
            company_records=company_records
        )

        # Step 7: Placement Readiness Scoring
        readiness_res = PlacementReadinessEngine.calculate_readiness_score(
            candidate_skills=info_res["all_skills"],
            candidate_cgpa=candidate_cgpa,
            candidate_projects=projects,
            candidate_experience=experience,
            candidate_certifications=certifications,
            company_matches=company_matches,
            frequency_data=freq_data
        )

        # Step 8: LLM Gap Analysis (reusing existing LLM)
        llm_insights = await generate_llm_resume_analysis(
            candidate_name=candidate_name,
            education_info=education_info,
            skills_data=skills_data,
            matched_skills=matched_skills,
            partial_skills=partial_skills,
            missing_skills=missing_skills,
            priority_missing=priority_missing,
            top_company_matches=company_matches,
            projects=projects,
            readiness_data=readiness_res
        )

        # Step 9: Personalized Improvement Plan
        improvement_plan = PersonalizedPlanBuilder.generate_plan(
            missing_skills=missing_skills,
            partial_skills=partial_skills,
            priority_tiers=priority_missing,
            projects=projects,
            experience=experience
        )

        # Step 10: Optional DB Persistence
        saved_id = None
        if save_to_db:
            try:
                saved_id = DatabaseService.save_resume_analysis(
                    student_id=student_id,
                    student_name=candidate_name,
                    filename=filename or "resume_upload",
                    extracted_info={
                        "personal": info_res["personal"],
                        "education": education_info,
                        "skills": skills_data,
                        "projects": projects,
                        "experience": experience,
                        "certifications": certifications,
                        "quality": quality_analysis
                    },
                    matched_skills=matched_skills,
                    partial_skills=partial_skills,
                    missing_skills=missing_skills,
                    readiness_score=readiness_res["readiness_score"],
                    readiness_level=readiness_res["readiness_level"],
                    company_matches=company_matches[:10],
                    llm_analysis=llm_insights
                )
            except Exception as e:
                print(f"Warning: Failed to save resume analysis to database: {e}")

        return {
            "status": "success",
            "saved_id": saved_id,
            "filename": filename,
            "candidate_name": candidate_name,
            "education": education_info,
            "contact": info_res["personal"]["contact"],
            "skills_inventory": skills_data,
            "projects": projects,
            "experience": experience,
            "certifications": certifications,
            "resume_quality": quality_analysis,
            "recruitment_dataset": {
                "available": rec_status["available"],
                "total_companies_in_dataset": rec_status["record_count"],
                "warning": dataset_warning
            },
            "skill_analysis": {
                "matched_skills": matched_skills,
                "partial_skills": partial_skills,
                "missing_skills": missing_skills,
                "total_matched": len(matched_skills),
                "total_partial": len(partial_skills),
                "total_missing": len(missing_skills)
            },
            "skill_priority": priority_missing,
            "market_frequencies": freq_data,
            "company_matching": company_matches,
            "placement_readiness": readiness_res,
            "llm_analysis": llm_insights,
            "personalized_improvement_plan": improvement_plan
        }
