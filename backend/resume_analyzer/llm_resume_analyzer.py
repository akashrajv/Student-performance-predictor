import os
import json
import httpx
from typing import Dict, Any, List, Optional
from backend.config import settings

def build_resume_system_prompt() -> str:
    return """You are an expert AI Career Coach and Technical Recruitment Advisor in the Student Performance & Placement System.
Your task is to analyze a student's resume against recruitment requirements, identify skill gaps, and provide a realistic, prioritized placement improvement plan.

CRITICAL RULES:
1. Ground every statement STRICTLY in the provided resume data, matched skills, missing skills, and recruitment dataset evidence.
2. DO NOT invent, hallucinate, or assume company requirements, skills, certifications, or projects not provided in the prompt.
3. DO NOT claim that placement is guaranteed or promise job offers.
4. Distinguish clearly between skills the student already possesses and skills they need to learn.
5. All recommendations must be realistic and actionable for an undergraduate college student.
6. Prioritize missing skills using the empirical recruitment frequencies provided.
7. Output MUST be valid JSON with the exact keys:
   - "resume_summary": A concise overview (2-3 sentences) of the candidate's profile and technical orientation.
   - "main_strengths": A list of 3-4 key technical strengths demonstrated in the resume.
   - "important_skill_gaps": A list of 3-4 notable missing or partially matched skills that hinder placement readiness.
   - "high_priority_skills_to_learn": A list of 2-3 specific skills with high company demand to prioritize immediately.
   - "project_improvement_suggestions": A list of 2-3 concrete suggestions to improve existing projects or build new portfolio projects.
   - "resume_improvement_suggestions": A list of 2-3 specific formatting, phrasing, or content improvements for the resume document.
   - "company_specific_preparation_advice": A list of 2-3 actionable tips targeting specific companies/roles in the recruitment dataset.
   - "short_term_improvement_plan": A list of 3-4 actions for the next 2-4 weeks (e.g. foundational practice, DSA, key syntax).
   - "medium_term_improvement_plan": A list of 3-4 actions for 1-3 months (e.g. full projects, mock interviews, certifications).
   - "placement_preparation_suggestions": A list of 2-3 placement drive preparation strategies (aptitude, mock interviews, system design basics).
"""

def build_resume_user_prompt(
    candidate_name: str,
    education_info: Dict[str, Any],
    skills_data: Dict[str, Any],
    matched_skills: List[str],
    partial_skills: List[str],
    missing_skills: List[str],
    priority_missing: Dict[str, List[Dict[str, Any]]],
    top_company_matches: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    readiness_data: Dict[str, Any]
) -> str:
    high_missing_str = ", ".join([f"{item['skill']} (Required by {item.get('frequency_count', 0)} companies)" for item in priority_missing.get("High Priority", [])[:5]])
    med_missing_str = ", ".join([f"{item['skill']} ({item.get('frequency_count', 0)} companies)" for item in priority_missing.get("Medium Priority", [])[:5]])

    top_comps_str = "\n".join([
        f"- {m.get('company')} ({m.get('role')}): Alignment = {m.get('alignment')} (Matched: {', '.join(m.get('matched_skills', [])[:3])} | Missing: {', '.join(m.get('missing_skills', [])[:3])})"
        for m in top_company_matches[:5]
    ])

    projects_str = "\n".join([
        f"- {p.get('title')}: Tech = {', '.join(p.get('technologies', []))} | Desc = {p.get('description', 'N/A')}"
        for p in projects[:3]
    ]) or "No distinct technical projects detected."

    return f"""CANDIDATE RESUME PROFILE:
Candidate Name: {candidate_name}
Degree & Department: {education_info.get('degree', 'N/A')} - {education_info.get('branch', 'N/A')}
College: {education_info.get('college', 'N/A')}
Academic CGPA/Score: {education_info.get('cgpa', 'N/A')}

DETECTED SKILLS IN RESUME:
{', '.join(skills_data.get('all_skills', [])[:20]) or 'Limited skills identified'}

PROGRAMMATIC MATCHING RESULTS (Deterministic Ground Truth):
- Matched Skills: {', '.join(matched_skills) or 'None'}
- Partially Matched Skills: {', '.join(partial_skills) or 'None'}
- Missing Skills: {', '.join(missing_skills[:15]) or 'None'}

EMPIRICAL RECRUITMENT MARKET PRIORITY (Source of Truth):
- High-Priority Missing Skills: {high_missing_str or 'None'}
- Medium-Priority Missing Skills: {med_missing_str or 'None'}

RECRUITMENT COMPANY & ROLE ALIGNMENT:
{top_comps_str or 'No direct company matches.'}

RELEVANT PROJECTS:
{projects_str}

PROJECT-DEFINED PLACEMENT READINESS:
- Score: {readiness_data.get('readiness_score', 0)}%
- Level: {readiness_data.get('readiness_level', 'Developing')}

Generate your analysis strictly as a valid JSON object matching the requested schema.
"""

def generate_grounded_resume_fallback(
    candidate_name: str,
    education_info: Dict[str, Any],
    skills_data: Dict[str, Any],
    matched_skills: List[str],
    partial_skills: List[str],
    missing_skills: List[str],
    priority_missing: Dict[str, List[Dict[str, Any]]],
    top_company_matches: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    readiness_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deterministic, grounded fallback career advisory engine.
    Ensures structured, high-value feedback when external LLM APIs are offline or without API key.
    """
    name = candidate_name if candidate_name != "Unknown Candidate" else "The candidate"
    all_cand_skills = skills_data.get("all_skills", [])
    high_missing = [item["skill"] for item in priority_missing.get("High Priority", [])]
    med_missing = [item["skill"] for item in priority_missing.get("Medium Priority", [])]

    # Strengths
    strengths = []
    if matched_skills:
        strengths.append(f"Demonstrated command of core recruitment technologies: {', '.join(matched_skills[:4])}.")
    if len(all_cand_skills) >= 6:
        strengths.append(f"Broad foundational skill inventory spanning {len(all_cand_skills)} recognized technical tools.")
    if projects:
        strengths.append(f"Practical portfolio containing {len(projects)} tangible technical projects.")
    if not strengths:
        strengths.append("Foundational academic training in engineering fundamentals.")

    # Gaps
    gaps = []
    if high_missing:
        gaps.append(f"High-frequency campus recruitment requirements missing: {', '.join(high_missing[:3])}.")
    if partial_skills:
        gaps.append(f"Partial foundations requiring formalization: {', '.join(partial_skills[:3])}.")
    if not projects or len(projects) < 2:
        gaps.append("Limited depth in end-to-end deployed portfolio projects.")
    if not gaps:
        gaps.append("Continuous competitive problem solving and system design practice.")

    # High priority to learn
    to_learn = high_missing[:3] if high_missing else (med_missing[:3] if med_missing else ["SQL", "Data Structures", "Docker"])

    # Project suggestions
    proj_sugg = []
    if "Docker" in missing_skills or "Cloud" in missing_skills or "AWS" in missing_skills:
        proj_sugg.append("Containerize an existing application using Docker and deploy it to a free-tier cloud instance (AWS/GCP) with CI/CD.")
    if "SQL" in missing_skills or "Database" in missing_skills:
        proj_sugg.append("Build a database-driven CRUD application utilizing relational schema design, indexing, and complex SQL joins.")
    if "Machine Learning" in missing_skills or "Data Analysis" in missing_skills:
        proj_sugg.append("Implement an end-to-end data pipeline with exploratory analysis, scikit-learn models, and an interactive dashboard.")
    if not proj_sugg:
        proj_sugg.append("Develop a full-stack project incorporating REST API endpoints, user authentication, and unit testing.")
        proj_sugg.append("Add clear architectural diagrams and quantifiable metrics (latency, user count, test coverage) to project READMEs.")

    # Resume improvements
    res_sugg = [
        "Structure bullet points using the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'.",
        "Place your strongest technical skills and verified projects prominently near the top of the resume.",
        "Include live GitHub repository links and deployed project demonstration URLs for every listed project."
    ]

    # Company specific advice
    comp_advice = []
    for comp in top_company_matches[:3]:
        c_name = comp.get("company", "Tech Company")
        c_role = comp.get("role", "Software Role")
        c_miss = comp.get("missing_skills", [])
        if c_miss:
            comp_advice.append(f"For {c_name} ({c_role}): Focus preparation on {', '.join(c_miss[:2])} and practice role-specific technical assessments.")
        else:
            comp_advice.append(f"For {c_name} ({c_role}): Strong technical alignment; prioritize standard Data Structures & Algorithms coding rounds.")

    # Timeline plans
    short_term = [
        f"Master foundational concepts and hands-on coding in {to_learn[0] if to_learn else 'Core Data Structures'}.",
        "Solve 20-25 targeted LeetCode/HackerRank easy-to-medium problems on Arrays, Strings, and Hash Maps.",
        "Revise resume project descriptions to highlight individual architectural contributions."
    ]

    medium_term = [
        f"Complete a comprehensive project incorporating {', '.join(to_learn[:2])} and publish source code with documentation.",
        "Participate in weekly timed mock technical and HR interviews with peers or mentors.",
        "Review core Computer Science fundamentals: Operating Systems, Computer Networks, and DBMS."
    ]

    prep_sugg = [
        "Dedicate 45 minutes daily to quantitative aptitude and logical reasoning assessments commonly used in round-one screening.",
        "Prepare structured 2-minute elevator pitches for your top two portfolio projects explaining technical tradeoffs."
    ]

    summary = (
        f"{name} presents a {readiness_data.get('readiness_level', 'developing')} profile with {len(all_cand_skills)} "
        f"demonstrated skills. While solid foundations exist in {', '.join(matched_skills[:2]) if matched_skills else 'academics'}, "
        f"targeted upskilling in high-frequency recruitment competencies ({', '.join(to_learn)}) will substantially strengthen placement conversion."
    )

    return {
        "resume_summary": summary,
        "main_strengths": strengths,
        "important_skill_gaps": gaps,
        "high_priority_skills_to_learn": to_learn,
        "project_improvement_suggestions": proj_sugg,
        "resume_improvement_suggestions": res_sugg,
        "company_specific_preparation_advice": comp_advice,
        "short_term_improvement_plan": short_term,
        "medium_term_improvement_plan": medium_term,
        "placement_preparation_suggestions": prep_sugg,
        "model_used": "Grounded-Resume-Engine (Deterministic Ground Truth)"
    }

async def generate_llm_resume_analysis(
    candidate_name: str,
    education_info: Dict[str, Any],
    skills_data: Dict[str, Any],
    matched_skills: List[str],
    partial_skills: List[str],
    missing_skills: List[str],
    priority_missing: Dict[str, List[Dict[str, Any]]],
    top_company_matches: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    readiness_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Reuses existing LLM provider (Gemini / OpenAI / Ollama) configured in project settings.
    Seamlessly falls back to deterministic grounded engine if offline or API key missing.
    """
    api_key = os.getenv("LLM_API_KEY", settings.LLM_API_KEY).strip()
    provider = os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER).lower()
    model_name = os.getenv("LLM_MODEL", settings.LLM_MODEL)

    # If no API key provided, use grounded fallback
    if not api_key and provider != "ollama":
        return generate_grounded_resume_fallback(
            candidate_name=candidate_name,
            education_info=education_info,
            skills_data=skills_data,
            matched_skills=matched_skills,
            partial_skills=partial_skills,
            missing_skills=missing_skills,
            priority_missing=priority_missing,
            top_company_matches=top_company_matches,
            projects=projects,
            readiness_data=readiness_data
        )

    system_prompt = build_resume_system_prompt()
    user_prompt = build_resume_user_prompt(
        candidate_name=candidate_name,
        education_info=education_info,
        skills_data=skills_data,
        matched_skills=matched_skills,
        partial_skills=partial_skills,
        missing_skills=missing_skills,
        priority_missing=priority_missing,
        top_company_matches=top_company_matches,
        projects=projects,
        readiness_data=readiness_data
    )

    try:
        # 1. Google Gemini Provider
        if provider in ["gemini", "auto"] and (api_key.startswith("AIza") or api_key.startswith("AQ.") or "gemini" in model_name or provider == "gemini"):
            active_model = model_name
            if active_model in ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]:
                active_model = "gemini-3.5-flash-lite"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text)
                    parsed["model_used"] = f"Gemini ({active_model})"
                    return parsed

        # 2. OpenAI Provider
        if provider in ["openai", "auto"] and (api_key.startswith("sk-") or "gpt" in model_name):
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name if "gpt" in model_name else "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    parsed = json.loads(text)
                    parsed["model_used"] = f"OpenAI ({model_name})"
                    return parsed

        # 3. Ollama Provider
        if provider == "ollama":
            url = f"{settings.OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": model_name or "llama3",
                "prompt": f"{system_prompt}\n\n{user_prompt}\nRespond with JSON only.",
                "stream": False,
                "format": "json"
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    parsed = json.loads(data["response"])
                    parsed["model_used"] = f"Ollama ({model_name})"
                    return parsed

    except Exception as e:
        print(f"External LLM API call error during resume analysis: {e}. Falling back to grounded engine.")

    # Graceful fallback on API error or invalid response
    fallback = generate_grounded_resume_fallback(
        candidate_name=candidate_name,
        education_info=education_info,
        skills_data=skills_data,
        matched_skills=matched_skills,
        partial_skills=partial_skills,
        missing_skills=missing_skills,
        priority_missing=priority_missing,
        top_company_matches=top_company_matches,
        projects=projects,
        readiness_data=readiness_data
    )
    fallback["model_used"] = "Grounded-Resume-Engine (API Fallback)"
    return fallback
