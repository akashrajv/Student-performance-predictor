from typing import Dict, Any, List

# Curated actionable roadmaps for top technologies
SKILL_ACTION_GUIDES: Dict[str, Dict[str, str]] = {
    "sql": {
        "title": "Master Relational Databases & SQL Queries",
        "action": "Strengthen SQL fundamentals (DDL, DML, multi-table JOINs, subqueries, group by, indexing, and window functions). Complete practical query challenges on LeetCode/HackerRank.",
        "project_suggestion": "Build an e-commerce or student management schema with normalized tables, write complex analytical queries, and connect it to a backend application."
    },
    "python": {
        "title": "Core Python & Algorithmic Problem Solving",
        "action": "Solidify object-oriented programming, data structures (lists, dicts, sets, heaps), list comprehensions, and standard libraries. Practice 25+ algorithmic challenges.",
        "project_suggestion": "Develop an automated data processing script or backend microservice utilizing Python typing, logging, and unit tests."
    },
    "java": {
        "title": "Java Fundamentals & Object-Oriented Design",
        "action": "Review Core Java concepts: OOP principles, Collections Framework, multithreading basics, Exception Handling, and JVM memory lifecycle.",
        "project_suggestion": "Create a console or Spring Boot application implementing design patterns (Factory, Singleton, Repository)."
    },
    "data structures": {
        "title": "Data Structures & Algorithmic Foundations (DSA)",
        "action": "Implement fundamental data structures from scratch: Arrays, Linked Lists, Stacks, Queues, Binary Trees, and Hash Tables. Focus on Big-O time and space complexity.",
        "project_suggestion": "Complete a 30-day curated coding streak solving 2 problems daily covering two-pointer technique, sliding window, and tree traversals."
    },
    "docker": {
        "title": "Containerization with Docker",
        "action": "Learn Docker basics: Dockerfiles, multi-stage builds, container images, volume mapping, port binding, and Docker Compose for multi-container orchestration.",
        "project_suggestion": "Containerize an existing web application and database, create a docker-compose.yml file, and write a setup guide."
    },
    "aws": {
        "title": "Cloud Fundamentals on AWS",
        "action": "Understand core cloud computing architecture: EC2 instances, S3 object storage, IAM access control, RDS databases, and basic VPC networking concepts.",
        "project_suggestion": "Deploy a containerized application to AWS Elastic Beanstalk or EC2, configure an S3 bucket for static media, and enable HTTPS."
    },
    "react": {
        "title": "Modern Frontend Development with React",
        "action": "Master component lifecycles, hooks (useState, useEffect, useMemo, useCallback), context API, and state management. Practice responsive UI design.",
        "project_suggestion": "Construct a responsive dashboard featuring data fetching from a REST API, client-side routing, and search/filter controls."
    },
    "machine learning": {
        "title": "Applied Machine Learning & Model Evaluation",
        "action": "Master data preprocessing, feature engineering, train/test splitting, cross-validation, and performance metrics (Precision, Recall, F1, ROC-AUC) using scikit-learn.",
        "project_suggestion": "Build an end-to-end predictive machine learning model pipeline on a real tabular dataset with Explainable AI feature attributions and deploy as a web app."
    },
    "git": {
        "title": "Version Control & Collaborative Git Workflows",
        "action": "Master Git branching strategies, pull requests, resolving merge conflicts, rebasing, and conventional commit messages.",
        "project_suggestion": "Maintain clean GitHub repository history with feature branches, detailed README markdown, issue templates, and GitHub Actions CI."
    },
    "spring boot": {
        "title": "Enterprise Backend with Spring Boot",
        "action": "Understand dependency injection, Spring MVC, Spring Data JPA, RESTful API controllers, and secure endpoint handling.",
        "project_suggestion": "Build a modular REST API with database persistence, pagination, validation, and Swagger/OpenAPI documentation."
    }
}

class PersonalizedPlanBuilder:
    """
    Constructs concrete, prioritized improvement steps grounded directly
    in the candidate's actual missing skills and identified project gaps.
    """

    @classmethod
    def generate_plan(
        cls,
        missing_skills: List[str],
        partial_skills: List[str],
        priority_tiers: Dict[str, List[Dict[str, Any]]],
        projects: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
        llm_plan_items: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Produce a list of structured Priority 1, Priority 2, Priority 3, Priority 4 cards.
        """
        plan_cards = []
        p_index = 1

        # Check high-priority missing skills from recruitment dataset
        high_missing = [item["skill"] for item in priority_tiers.get("High Priority", [])]
        med_missing = [item["skill"] for item in priority_tiers.get("Medium Priority", [])]

        # 1. Primary High-Priority Technical Gap
        primary_gap = high_missing[0] if high_missing else (missing_skills[0] if missing_skills else None)
        if primary_gap:
            guide = cls._find_guide_for_skill(primary_gap)
            plan_cards.append({
                "priority_level": f"Priority {p_index}",
                "priority_num": p_index,
                "gap_type": "High-Demand Technical Skill Gap",
                "missing_skill": primary_gap,
                "title": guide["title"],
                "action": guide["action"],
                "project_recommendation": guide["project_suggestion"],
                "timeline": "Weeks 1 - 2"
            })
            p_index += 1

        # 2. Secondary High/Medium Priority Gap
        secondary_gap = high_missing[1] if len(high_missing) > 1 else (med_missing[0] if med_missing else (missing_skills[1] if len(missing_skills) > 1 else None))
        if secondary_gap:
            guide = cls._find_guide_for_skill(secondary_gap)
            plan_cards.append({
                "priority_level": f"Priority {p_index}",
                "priority_num": p_index,
                "gap_type": "Recruitment Requirement Gap",
                "missing_skill": secondary_gap,
                "title": guide["title"],
                "action": guide["action"],
                "project_recommendation": guide["project_suggestion"],
                "timeline": "Weeks 3 - 4"
            })
            p_index += 1

        # 3. Practical Portfolio & Hands-on Implementation Gap
        if len(projects) < 2:
            tech_target = primary_gap or "Full Stack Web & Database"
            plan_cards.append({
                "priority_level": f"Priority {p_index}",
                "priority_num": p_index,
                "gap_type": "Portfolio Depth Gap",
                "missing_skill": f"Applied {tech_target} Project",
                "title": f"Build & Deploy an End-to-End {tech_target} Project",
                "action": "Recruiters prioritize demonstrable practical implementations. Develop a complete application with source code hosted publicly on GitHub and a live deployment link.",
                "project_recommendation": f"Design an end-to-end system utilizing {tech_target}, complete with structured README documentation, architecture diagrams, and test cases.",
                "timeline": "Weeks 4 - 6"
            })
            p_index += 1
        elif partial_skills:
            p_gap = partial_skills[0]
            guide = cls._find_guide_for_skill(p_gap)
            plan_cards.append({
                "priority_level": f"Priority {p_index}",
                "priority_num": p_index,
                "gap_type": "Partial Skill Solidification",
                "missing_skill": p_gap,
                "title": f"Elevate Foundational Knowledge in {p_gap}",
                "action": f"Formalize existing exposure into industry-grade competence. {guide['action']}",
                "project_recommendation": guide["project_suggestion"],
                "timeline": "Weeks 4 - 6"
            })
            p_index += 1

        # 4. Placement Drive & Technical Interview Preparation
        plan_cards.append({
            "priority_level": f"Priority {p_index}",
            "priority_num": p_index,
            "gap_type": "Campus Placement Drive Readiness",
            "missing_skill": "Technical Interview & Aptitude Execution",
            "title": "Aptitude, Core CS Subjects & Mock Technical Rounds",
            "action": "Consistent daily practice on quantitative aptitude, logical reasoning, and verbal ability. Review Core CS subjects (DBMS, OS, Computer Networks). Conduct peer mock coding interviews.",
            "project_recommendation": "Prepare 2-minute project walkthroughs describing architectural decisions, technical challenges faced, and quantifiable results.",
            "timeline": "Ongoing (Daily 45 mins)"
        })

        return plan_cards

    @classmethod
    def _find_guide_for_skill(cls, skill: str) -> Dict[str, str]:
        s_low = skill.lower().strip()
        for k, v in SKILL_ACTION_GUIDES.items():
            if k in s_low or s_low in k:
                return v

        return {
            "title": f"Strengthen Competencies in {skill}",
            "action": f"Master core syntax, fundamental concepts, and standard tooling for {skill}. Complete hands-on coding tutorials and review documentation.",
            "project_suggestion": f"Incorporate {skill} into an existing or new portfolio project, demonstrating functional understanding and practical utility."
        }
