import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import pandas as pd

from backend.config import settings

def normalize_skill_name(skill: str) -> str:
    """Normalize skill string by trimming whitespace and standardizing common casing."""
    if not skill:
        return ""
    cleaned = re.sub(r'[\r\n\t]', ' ', str(skill)).strip()
    cleaned = re.sub(r'^[•\-\*#]+\s*', '', cleaned).strip()
    # Handle known casing standardizations
    title_cases = {
        "sql": "SQL", "mysql": "MySQL", "postgresql": "PostgreSQL",
        "aws": "AWS", "gcp": "GCP", "azure": "Azure", "html": "HTML", "css": "CSS",
        "api": "API", "rest api": "REST API", "graphql": "GraphQL",
        "ci/cd": "CI/CD", "c++": "C++", "c#": "C#", "php": "PHP",
        "nlp": "NLP", "llm": "LLM", "ai": "AI", "ml": "Machine Learning",
        "dsa": "Data Structures", "dbms": "DBMS", "oop": "OOP", "rtos": "RTOS",
        "ccna": "CCNA", "json": "JSON"
    }
    low = cleaned.lower()
    if low in title_cases:
        return title_cases[low]
    # Return title-cased or preserve original if mixed case (like JavaScript, React)
    if cleaned.islower() or cleaned.isupper():
        return cleaned.title()
    return cleaned

class RecruitmentDatasetAnalyzer:
    """
    Dynamic analyzer for recruitment dataset with automated schema detection.
    Does not assume fixed column names.
    Calculates empirical requirement frequencies directly from source data.
    """

    def __init__(self, data_source: Optional[Union_source] = None):
        pass

Union_source = Any  # helper type

class RecruitmentAnalyzer:
    """
    Source-of-truth analyzer for company requirements and skill frequency priority.
    """

    def __init__(self, dataset_path: Optional[Path] = None, df_override: Optional[pd.DataFrame] = None):
        self.dataset_path = dataset_path or settings.RECRUITMENT_DATA_PATH
        self.df: Optional[pd.DataFrame] = None
        self.column_map: Dict[str, Optional[str]] = {}
        self.is_loaded: bool = False
        self.error_message: Optional[str] = None
        
        # Load and detect schema
        self._load_and_detect_schema(df_override)

    def _load_and_detect_schema(self, df_override: Optional[pd.DataFrame] = None):
        """Load the dataset and automatically identify the column schema."""
        if df_override is not None:
            self.df = df_override.copy()
            self.is_loaded = True
        elif self.dataset_path and Path(self.dataset_path).exists():
            try:
                self.df = pd.read_csv(self.dataset_path)
                self.is_loaded = True
            except Exception as e:
                self.error_message = f"Failed to parse recruitment dataset CSV: {str(e)}"
                self.is_loaded = False
                return
        else:
            self.error_message = (
                f"Recruitment dataset not found at '{self.dataset_path}'. "
                "Please ensure recruitment_data.csv is present or upload a recruitment dataset."
            )
            self.is_loaded = False
            return

        if self.df is None or self.df.empty:
            self.error_message = "Recruitment dataset is empty (0 records)."
            self.is_loaded = False
            return

        # Automatic schema detection
        cols = {col.lower().strip().replace(" ", "_"): col for col in self.df.columns}

        def find_matching_col(patterns: List[str]) -> Optional[str]:
            for p in patterns:
                for norm_c, orig_c in cols.items():
                    if p in norm_c or norm_c in p:
                        return orig_c
            return None

        self.column_map = {
            "company": find_matching_col(["company", "company_name", "employer", "organization", "firm"]),
            "role": find_matching_col(["job_role", "role", "position", "title", "job_title", "designation"]),
            "department": find_matching_col(["department", "dept", "branch", "eligible_branches", "domain", "stream"]),
            "cgpa": find_matching_col(["min_cgpa", "cgpa", "cutoff", "minimum_cgpa", "cgpa_requirement", "gpa"]),
            "required_skills": find_matching_col(["required_skills", "mandatory_skills", "core_skills", "skills", "technical_skills"]),
            "preferred_skills": find_matching_col(["preferred_skills", "desired_skills", "good_to_have", "bonus_skills", "secondary_skills"]),
            "certifications": find_matching_col(["certifications", "preferred_certifications", "certs", "certification"]),
            "eligibility": find_matching_col(["eligibility_criteria", "eligibility", "criteria", "requirements", "eligibility_requirements"])
        }

        # Fallback if required_skills not detected but a generic 'skills' exists
        if not self.column_map["required_skills"]:
            for norm_c, orig_c in cols.items():
                if "skill" in norm_c:
                    self.column_map["required_skills"] = orig_c
                    break

    def get_status(self) -> Dict[str, Any]:
        """Return loading status and detected schema details."""
        if not self.is_loaded:
            return {
                "available": False,
                "error": self.error_message,
                "record_count": 0,
                "detected_columns": {}
            }
        return {
            "available": True,
            "error": None,
            "record_count": len(self.df) if self.df is not None else 0,
            "detected_columns": {k: v for k, v in self.column_map.items() if v is not None},
            "source_path": str(self.dataset_path)
        }

    def _split_skills(self, cell_value: Any) -> List[str]:
        """Split a skill cell into individual normalized skill tokens."""
        if pd.isna(cell_value) or not cell_value:
            return []
        val_str = str(cell_value)
        # Split by commas, semicolons, pipes, or newlines
        tokens = re.split(r'[,;|\n\r]+', val_str)
        skills = []
        for t in tokens:
            norm = normalize_skill_name(t)
            if norm and len(norm) > 1 and norm.lower() not in ["none", "na", "n/a", "nil", "none required"]:
                skills.append(norm)
        return skills

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Return all recruitment opportunities with normalized fields."""
        if not self.is_loaded or self.df is None:
            return []

        records = []
        comp_col = self.column_map.get("company")
        role_col = self.column_map.get("role")
        dept_col = self.column_map.get("department")
        cgpa_col = self.column_map.get("cgpa")
        req_col = self.column_map.get("required_skills")
        pref_col = self.column_map.get("preferred_skills")
        cert_col = self.column_map.get("certifications")
        elig_col = self.column_map.get("eligibility")

        for idx, row in self.df.iterrows():
            comp_name = str(row[comp_col]).strip() if comp_col and not pd.isna(row[comp_col]) else f"Company #{idx+1}"
            job_role = str(row[role_col]).strip() if role_col and not pd.isna(row[role_col]) else "Technology Specialist"
            dept = str(row[dept_col]).strip() if dept_col and not pd.isna(row[dept_col]) else "Any Department"
            
            # CGPA parsing
            min_cgpa = None
            if cgpa_col and not pd.isna(row[cgpa_col]):
                try:
                    min_cgpa = float(row[cgpa_col])
                except (ValueError, TypeError):
                    min_cgpa = None

            req_skills = self._split_skills(row[req_col]) if req_col else []
            pref_skills = self._split_skills(row[pref_col]) if pref_col else []
            certs = str(row[cert_col]).strip() if cert_col and not pd.isna(row[cert_col]) else "None Specified"
            elig = str(row[elig_col]).strip() if elig_col and not pd.isna(row[elig_col]) else "Standard campus eligibility criteria apply"

            records.append({
                "record_id": idx + 1,
                "company": comp_name,
                "role": job_role,
                "department": dept,
                "min_cgpa": min_cgpa,
                "required_skills": req_skills,
                "preferred_skills": pref_skills,
                "all_role_skills": sorted(list(set(req_skills + pref_skills))),
                "certifications": certs,
                "eligibility": elig
            })

        return records

    def calculate_skill_frequencies(self) -> Dict[str, Any]:
        """
        Compute empirical requirement frequency across all recruitment postings.
        Returns:
            - frequency_counts: {skill: count}
            - frequency_percentages: {skill: percentage of total postings}
            - priority_tiers: {"High Priority": [...], "Medium Priority": [...], "Low Priority": [...]}
        """
        if not self.is_loaded or self.df is None or self.df.empty:
            return {
                "total_companies": 0,
                "frequency_counts": {},
                "frequency_percentages": {},
                "priority_tiers": {"High Priority": [], "Medium Priority": [], "Low Priority": []}
            }

        records = self.get_all_records()
        total_postings = len(records)
        freq_counts: Dict[str, int] = {}
        req_counts: Dict[str, int] = {}

        for rec in records:
            # Count each skill once per posting
            seen_in_posting: Set[str] = set()
            for sk in rec["required_skills"]:
                sk_norm = sk.strip()
                if sk_norm and sk_norm.lower() not in seen_in_posting:
                    freq_counts[sk_norm] = freq_counts.get(sk_norm, 0) + 1
                    req_counts[sk_norm] = req_counts.get(sk_norm, 0) + 1
                    seen_in_posting.add(sk_norm.lower())

            for sk in rec["preferred_skills"]:
                sk_norm = sk.strip()
                if sk_norm and sk_norm.lower() not in seen_in_posting:
                    freq_counts[sk_norm] = freq_counts.get(sk_norm, 0) + 1
                    seen_in_posting.add(sk_norm.lower())

        # Calculate percentages
        freq_percentages: Dict[str, float] = {}
        for sk, cnt in freq_counts.items():
            freq_percentages[sk] = round((cnt / total_postings) * 100, 1)

        # Sort by frequency descending
        sorted_skills = sorted(freq_counts.items(), key=lambda x: x[1], reverse=True)

        # Categorize into High, Medium, Low based on empirical thresholds
        # High Priority: >= 30% of companies require or top tier
        # Medium Priority: 15% - 29%
        # Low Priority: < 15%
        high_priority = []
        medium_priority = []
        low_priority = []

        for sk, count in sorted_skills:
            pct = freq_percentages[sk]
            item = {
                "skill": sk,
                "count": count,
                "percentage": pct,
                "total_postings": total_postings,
                "required_count": req_counts.get(sk, 0)
            }
            if pct >= 30.0:
                high_priority.append(item)
            elif pct >= 15.0:
                medium_priority.append(item)
            else:
                low_priority.append(item)

        return {
            "total_companies": total_postings,
            "frequency_counts": freq_counts,
            "frequency_percentages": freq_percentages,
            "priority_tiers": {
                "High Priority": high_priority,
                "Medium Priority": medium_priority,
                "Low Priority": low_priority
            }
        }
