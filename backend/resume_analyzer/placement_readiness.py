import re
from typing import Dict, Any, List, Optional
from backend.resume_analyzer.skill_matcher import SkillMatcher

DISCLAIMER_TEXT = (
    "Note: The Placement Readiness Score is a project-defined educational guidance indicator "
    "calculated from current skill alignment, project depth, and campus recruitment dataset benchmarks. "
    "It does not represent a commercial guarantee of hiring or placement probability."
)

class PlacementReadinessEngine:
    """
    Evaluates company/role alignment and computes the Project-defined Placement Readiness Score.
    """

    @classmethod
    def match_against_company(
        cls,
        candidate_skills: List[str],
        candidate_cgpa: Optional[float],
        candidate_projects: List[Dict[str, Any]],
        company_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match candidate against a single company/role record."""
        req_skills = company_record.get("required_skills", [])
        pref_skills = company_record.get("preferred_skills", [])
        all_reqs = req_skills if req_skills else pref_skills

        # Skill matching
        match_res = SkillMatcher.match_resume_against_skills(candidate_skills, all_reqs)
        matched = match_res["matched_skills"]
        partial = match_res["partial_skills"]
        missing = match_res["missing_skills"]
        score = match_res["match_score"]

        # Alignment level
        if score >= 70.0:
            alignment = "High Alignment"
        elif score >= 40.0:
            alignment = "Moderate Alignment"
        else:
            alignment = "Low Alignment"

        # Check CGPA eligibility if available
        min_cgpa = company_record.get("min_cgpa")
        cgpa_eligible = None
        cgpa_note = "CGPA criteria not specified"

        if min_cgpa is not None:
            if candidate_cgpa is not None:
                if candidate_cgpa >= min_cgpa:
                    cgpa_eligible = True
                    cgpa_note = f"Eligible (Candidate CGPA: {candidate_cgpa} ≥ Cutoff: {min_cgpa})"
                else:
                    cgpa_eligible = False
                    cgpa_note = f"Below Cutoff (Candidate CGPA: {candidate_cgpa} < Cutoff: {min_cgpa})"
            else:
                cgpa_note = f"Requires minimum CGPA of {min_cgpa} (Candidate CGPA not specified)"

        return {
            "company": company_record.get("company", "Company"),
            "role": company_record.get("role", "Role"),
            "department": company_record.get("department", "Any"),
            "min_cgpa": min_cgpa,
            "cgpa_eligible": cgpa_eligible,
            "cgpa_note": cgpa_note,
            "eligibility_criteria": company_record.get("eligibility", ""),
            "certifications_preferred": company_record.get("certifications", ""),
            "matched_skills": matched,
            "partial_skills": partial,
            "missing_skills": missing,
            "match_score": score,
            "alignment": alignment,
            "required_skills_count": len(req_skills),
            "matched_count": len(matched),
            "partial_count": len(partial),
            "missing_count": len(missing)
        }

    @classmethod
    def evaluate_all_companies(
        cls,
        candidate_skills: List[str],
        candidate_cgpa: Optional[float],
        candidate_projects: List[Dict[str, Any]],
        company_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Evaluate candidate across all available company opportunities."""
        results = []
        for rec in company_records:
            eval_res = cls.match_against_company(
                candidate_skills=candidate_skills,
                candidate_cgpa=candidate_cgpa,
                candidate_projects=candidate_projects,
                company_record=rec
            )
            results.append(eval_res)

        # Sort by match_score descending
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

    @classmethod
    def calculate_readiness_score(
        cls,
        candidate_skills: List[str],
        candidate_cgpa: Optional[float],
        candidate_projects: List[Dict[str, Any]],
        candidate_experience: List[Dict[str, Any]],
        candidate_certifications: List[str],
        company_matches: List[Dict[str, Any]],
        frequency_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate the Project-defined Placement Readiness Score.
        Transparent weighted index combining:
        1. Core Requirement Coverage (45%)
        2. High-Priority Market Skill Adoption (20%)
        3. Project Depth & Practical Validation (15%)
        4. Internship & Industry Exposure (10%)
        5. Certifications & Academic Baseline (10%)
        """
        # 1. Core Requirement Coverage (45 pts)
        if company_matches:
            avg_match_score = sum(m["match_score"] for m in company_matches) / len(company_matches)
            score_req = min(45.0, (avg_match_score / 100.0) * 45.0)
        else:
            score_req = min(45.0, len(candidate_skills) * 3.5)

        # 2. High-Priority Market Skill Adoption (20 pts)
        high_prio_skills = [item["skill"].lower() for item in frequency_data.get("priority_tiers", {}).get("High Priority", [])]
        cand_lower = [s.lower() for s in candidate_skills]
        if high_prio_skills:
            matched_high = sum(1 for hp in high_prio_skills if any(hp in c or c in hp for c in cand_lower))
            ratio_high = matched_high / max(1, len(high_prio_skills))
            score_prio = min(20.0, ratio_high * 20.0)
        else:
            score_prio = 12.0

        # 3. Practical Projects (15 pts)
        proj_count = len(candidate_projects)
        if proj_count >= 3:
            score_proj = 15.0
        elif proj_count == 2:
            score_proj = 12.0
        elif proj_count == 1:
            score_proj = 8.0
        else:
            score_proj = 2.0

        # 4. Experience & Internships (10 pts)
        exp_count = len(candidate_experience)
        if exp_count >= 2:
            score_exp = 10.0
        elif exp_count == 1:
            score_exp = 7.0
        else:
            score_exp = 2.0

        # 5. Certifications & Academic Standing (10 pts)
        score_academic = 0.0
        if candidate_certifications:
            score_academic += 5.0
        if candidate_cgpa is not None:
            if candidate_cgpa >= 7.5:
                score_academic += 5.0
            elif candidate_cgpa >= 6.5:
                score_academic += 3.5
            else:
                score_academic += 2.0
        else:
            score_academic += 3.0

        total_score = round(score_req + score_prio + score_proj + score_exp + score_academic, 1)
        total_score = min(100.0, max(5.0, total_score))

        # Readiness Tier
        if total_score >= 80.0:
            level = "Placement Ready (High Competitive Alignment)"
            badge_color = "green"
            summary_desc = "Profile demonstrates comprehensive skill coverage with strong project depth and competitive readiness."
        elif total_score >= 60.0:
            level = "Promising Candidate (Targeted Skill Gaps Identified)"
            badge_color = "amber"
            summary_desc = "Strong foundational capabilities; addressing 2-3 specific high-priority requirements will maximize placement conversion."
        elif total_score >= 40.0:
            level = "Developing Profile (Core Technical Foundations Needed)"
            badge_color = "orange"
            summary_desc = "Baseline competencies present. Focus required on fundamental coding, practical projects, and core technologies."
        else:
            level = "Early Stage (Fundamental Preparation Required)"
            badge_color = "red"
            summary_desc = "Substantial skill acquisition and project building required to meet current campus recruitment benchmarks."

        # High Alignment Companies count
        high_align_comps = [m["company"] for m in company_matches if m["alignment"] == "High Alignment"]
        mod_align_comps = [m["company"] for m in company_matches if m["alignment"] == "Moderate Alignment"]

        return {
            "readiness_score": total_score,
            "readiness_level": level,
            "badge_color": badge_color,
            "summary_description": summary_desc,
            "score_breakdown": {
                "core_requirements_score": round(score_req, 1),
                "market_priority_score": round(score_prio, 1),
                "practical_projects_score": round(score_proj, 1),
                "internship_experience_score": round(score_exp, 1),
                "certifications_academic_score": round(score_academic, 1)
            },
            "high_alignment_companies_count": len(high_align_comps),
            "moderate_alignment_companies_count": len(mod_align_comps),
            "total_companies_evaluated": len(company_matches),
            "disclaimer": DISCLAIMER_TEXT
        }
