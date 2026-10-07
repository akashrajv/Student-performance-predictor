import re
from typing import Dict, Any, List, Set, Tuple, Optional

# Synonyms and Canonical Aliases
SKILL_SYNONYMS: Dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "golang": "go",
    "c++": "cpp",
    "c plus plus": "cpp",
    "c#": "csharp",
    "c sharp": "csharp",
    "reactjs": "react",
    "react.js": "react",
    "react": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "angularjs": "angular",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "expressjs": "express",
    "express": "express",
    "fastapi": "fastapi",
    "springboot": "spring boot",
    "spring": "spring boot",
    "postgres": "postgresql",
    "psql": "postgresql",
    "mssql": "sql",
    "mysql": "mysql",
    "sqlite": "sqlite",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "google cloud",
    "google cloud platform": "google cloud",
    "azure": "azure",
    "microsoft azure": "azure",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "tf": "tensorflow",
    "dsa": "data structures",
    "data structures and algorithms": "data structures",
    "data structures & algorithms": "data structures",
    "algorithms": "algorithms",
    "oop": "object-oriented programming",
    "oops": "object-oriented programming",
    "dbms": "dbms",
    "rest api": "rest api",
    "restful api": "rest api",
    "rest apis": "rest api",
    "ci cd": "ci/cd",
    "powerbi": "power bi",
    "power bi": "power bi"
}

# Related Skill Families for Partial Matching
SKILL_FAMILIES: Dict[str, List[str]] = {
    "machine learning": [
        "scikit-learn", "pandas", "numpy", "statistics", "data science",
        "predictive modeling", "tensorflow", "pytorch", "deep learning"
    ],
    "deep learning": [
        "tensorflow", "pytorch", "keras", "neural networks", "machine learning", "nlp", "computer vision"
    ],
    "artificial intelligence": [
        "machine learning", "deep learning", "nlp", "computer vision", "llm"
    ],
    "data science": [
        "python", "pandas", "numpy", "sql", "machine learning", "statistics", "data analysis", "tableau", "power bi"
    ],
    "full stack": [
        "react", "node.js", "javascript", "html", "css", "express", "django", "fastapi", "sql"
    ],
    "web technologies": [
        "html", "css", "javascript", "react", "angular", "vue", "rest api"
    ],
    "cloud computing": [
        "aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "linux"
    ],
    "devops": [
        "docker", "kubernetes", "ci/cd", "jenkins", "linux", "git", "terraform"
    ],
    "system design": [
        "distributed systems", "microservices", "object-oriented programming", "software engineering", "database management systems"
    ],
    "embedded systems": [
        "c", "cpp", "microcontrollers", "rtos", "computer architecture", "assembly"
    ],
    "distributed systems": [
        "microservices", "system design", "docker", "kubernetes", "kafka"
    ],
    "database management systems": [
        "sql", "mysql", "postgresql", "mongodb", "oracle", "dbms"
    ],
    "object-oriented programming": [
        "java", "cpp", "python", "csharp"
    ]
}

# Negative guards: Prevent false matches
FALSE_POSITIVE_GUARDS: Set[Tuple[str, str]] = {
    ("java", "javascript"),
    ("javascript", "java"),
    ("c", "c++"),
    ("c", "c#"),
    ("c", "css"),
    ("go", "google cloud"),
    ("r", "react"),
    ("html", "machine learning")
}

def clean_skill_for_comparison(skill: str) -> str:
    """Normalize skill string for exact or synonym matching."""
    s = skill.lower().strip()
    s = re.sub(r'[\(\)\[\]\{\}]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return SKILL_SYNONYMS.get(s, s)

class SkillMatcher:
    """
    Deterministic programmatic skill matching engine.
    Compares candidate resume skills against target recruitment requirements.
    Classifies skills into MATCHED, PARTIALLY MATCHED, and MISSING.
    """

    @staticmethod
    def is_negative_guard(candidate_skill: str, target_skill: str) -> bool:
        c = candidate_skill.lower().strip()
        t = target_skill.lower().strip()
        return (c, t) in FALSE_POSITIVE_GUARDS or (t, c) in FALSE_POSITIVE_GUARDS

    @classmethod
    def evaluate_skill_alignment(
        cls,
        target_skill: str,
        resume_skills: List[str]
    ) -> Tuple[str, Optional[str], str]:
        """
        Evaluate single target requirement against a list of candidate resume skills.
        Returns:
            (classification, matched_with_skill, reason)
            where classification is 'MATCHED', 'PARTIAL', or 'MISSING'
        """
        target_norm = clean_skill_for_comparison(target_skill)
        target_orig = target_skill.strip()

        # 1. Exact Match or Synonym Match
        for r_sk in resume_skills:
            if cls.is_negative_guard(r_sk, target_orig):
                continue
            r_norm = clean_skill_for_comparison(r_sk)
            if target_norm == r_norm:
                return ("MATCHED", r_sk, f"Exact match with '{r_sk}'")

        # 2. Strict Substring / Punctuation variations (e.g. "React.js" vs "React")
        for r_sk in resume_skills:
            if cls.is_negative_guard(r_sk, target_orig):
                continue
            r_norm = clean_skill_for_comparison(r_sk)
            # Boundary-safe substring
            if len(target_norm) > 3 and len(r_norm) > 3:
                if (f" {target_norm} " in f" {r_norm} ") or (f" {r_norm} " in f" {target_norm} "):
                    return ("MATCHED", r_sk, f"Direct variation match with '{r_sk}'")

        # 3. Partial Match: Related Family or Tech Stack Foundation
        # Check if target is a high-level skill category and resume has specific components
        target_family = SKILL_FAMILIES.get(target_norm)
        if target_family:
            for r_sk in resume_skills:
                r_norm = clean_skill_for_comparison(r_sk)
                if r_norm in target_family:
                    return ("PARTIAL", r_sk, f"Related foundation '{r_sk}' maps to {target_orig}")

        # Check if candidate has a related skill that covers part of the target
        for r_sk in resume_skills:
            r_norm = clean_skill_for_comparison(r_sk)
            cand_family = SKILL_FAMILIES.get(r_norm, [])
            if target_norm in cand_family:
                return ("PARTIAL", r_sk, f"Demonstrated background in '{r_sk}' provides partial foundation for {target_orig}")

        return ("MISSING", None, f"'{target_orig}' not detected in resume")

    @classmethod
    def match_resume_against_skills(
        cls,
        resume_skills: List[str],
        target_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Match candidate resume skills against a list of target requirement skills.
        Returns:
            - matched: List of matched skills
            - partial: List of partially matched skills with details
            - missing: List of missing skills
            - match_percentage: Core match ratio
        """
        matched = []
        partial = []
        missing = []

        seen_targets = set()
        for t_sk in target_skills:
            t_clean = t_sk.strip()
            if not t_clean or t_clean.lower() in seen_targets:
                continue
            seen_targets.add(t_clean.lower())

            status, matched_with, reason = cls.evaluate_skill_alignment(t_clean, resume_skills)
            if status == "MATCHED":
                matched.append({
                    "skill": t_clean,
                    "matched_with": matched_with,
                    "reason": reason
                })
            elif status == "PARTIAL":
                partial.append({
                    "skill": t_clean,
                    "partial_with": matched_with,
                    "reason": reason
                })
            else:
                missing.append({
                    "skill": t_clean,
                    "reason": reason
                })

        total_targets = len(seen_targets)
        match_score = (len(matched) + 0.5 * len(partial)) / total_targets * 100 if total_targets > 0 else 0.0

        return {
            "total_target_skills": total_targets,
            "matched_skills": [m["skill"] for m in matched],
            "matched_details": matched,
            "partial_skills": [p["skill"] for p in partial],
            "partial_details": partial,
            "missing_skills": [ms["skill"] for ms in missing],
            "missing_details": missing,
            "match_score": round(match_score, 1)
        }

    @classmethod
    def prioritize_missing_skills(
        cls,
        missing_skills: List[str],
        frequency_data: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Assign High, Medium, Low priority tiers to missing skills
        using empirical recruitment dataset requirement frequencies.
        """
        freq_counts = frequency_data.get("frequency_counts", {})
        freq_pcts = frequency_data.get("frequency_percentages", {})
        total_postings = frequency_data.get("total_companies", 1)

        high = []
        medium = []
        low = []

        for sk in missing_skills:
            # Case-insensitive lookup in freq_counts
            count = 0
            pct = 0.0
            for f_sk, cnt in freq_counts.items():
                if clean_skill_for_comparison(f_sk) == clean_skill_for_comparison(sk):
                    count = cnt
                    pct = freq_pcts.get(f_sk, round((cnt / total_postings) * 100, 1))
                    break

            item = {
                "skill": sk,
                "frequency_count": count,
                "frequency_percentage": pct,
                "total_companies": total_postings
            }

            if pct >= 30.0 or count >= 8:
                high.append(item)
            elif pct >= 15.0 or count >= 4:
                medium.append(item)
            else:
                low.append(item)

        # Sort each tier by frequency descending
        high.sort(key=lambda x: x["frequency_count"], reverse=True)
        medium.sort(key=lambda x: x["frequency_count"], reverse=True)
        low.sort(key=lambda x: x["frequency_count"], reverse=True)

        return {
            "High Priority": high,
            "Medium Priority": medium,
            "Low Priority": low
        }
