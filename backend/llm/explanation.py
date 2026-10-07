import os
import json
import httpx
from typing import Dict, Any, List
from backend.config import settings

def build_system_prompt() -> str:
    return """You are an expert AI Academic Advisor and Educational Data Scientist in the Student Performance Predictor system.
Your mission is to interpret machine learning predictions for a student's academic performance, explain the underlying causes, and provide practical, compassionate, and actionable interventions.

CRITICAL RULES:
1. Ground every claim STRICTLY in the provided student metrics and model feature attributions.
2. DO NOT invent, hallucinate, or assume any student data, personal history, or medical facts not explicitly provided.
3. Keep your tone constructive, professional, and supportive.
4. Output MUST be valid JSON with the exact keys:
   - "explanation": A clear summary (2-3 sentences) explaining the prediction in natural language for an educator or parent.
   - "possible_causes": A list of 2-4 specific reasons why the student is struggling or thriving, based ONLY on the numbers provided.
   - "attention_areas": A list of 2-3 specific subjects/habits needing immediate focus.
   - "personalized_recommendations": A list of 3-4 concrete academic recommendations for the student.
   - "early_interventions": A list of 2-3 actionable steps an educator or academic counselor should take immediately.
"""

def build_user_prompt(
    student_id: str,
    student_name: str,
    input_data: Dict[str, Any],
    predicted_class: str,
    confidence: Optional[float],
    risk_category: str,
    risk_score: float,
    contributing_factors: List[Dict[str, Any]],
    consensus: Optional[Dict[str, Any]] = None
) -> str:
    factors_summary = "\n".join([
        f"- {f.get('feature_name_clean')}: {f.get('value')} (Cohort benchmark: {f.get('benchmark')}, Impact: {f.get('impact')}) -> {f.get('description')}"
        for f in contributing_factors[:6]
    ])

    conf_display = f"{round(confidence * 100, 1)}%" if confidence is not None else "Confidence unavailable"

    consensus_section = ""
    if consensus:
        c_count = consensus.get("consensus_count", 0)
        c_total = consensus.get("total_models", 3)
        c_pct = consensus.get("consensus_percentage", 0.0)
        c_status = consensus.get("consensus_status", "N/A")
        c_avg_conf = consensus.get("average_confidence_display", "Confidence unavailable")
        c_final = consensus.get("final_prediction", risk_category)

        m_lines = []
        for m_name, m_data in consensus.get("model_predictions", {}).items():
            m_pred = m_data.get("prediction", "Unknown")
            m_conf = m_data.get("confidence_display", "Confidence unavailable")
            m_lines.append(f"  * {m_name}: {m_pred} (Confidence: {m_conf})")

        consensus_section = f"""
MODEL CONSENSUS (Multi-Model Agreement Layer):
- Final Risk Prediction: {c_final}
- Models Agree: {c_count} / {c_total}
- Consensus Percentage: {c_pct}%
- Consensus Status: {c_status}
- Average Model Confidence: {c_avg_conf}
- Individual Model Breakdown:
{chr(10).join(m_lines)}
- Important Note: 100% consensus indicates agreement across independent algorithms, not guaranteed accuracy.
"""

    return f"""STUDENT RECORD:
Student ID: {student_id}
Student Name: {student_name}
Input Metrics:
- Attendance: {input_data.get('Attendance_Percentage', input_data.get('attendance_percentage'))}%
- Study Hours/Week: {input_data.get('Study_Hours_Per_Week', input_data.get('study_hours_per_week'))} hrs
- Previous Grade: {input_data.get('Previous_Grade', input_data.get('previous_grade'))}/100
- Assignment Score: {input_data.get('Assignment_Score', input_data.get('assignment_score'))}/100
- Assessment Score: {input_data.get('Assessment_Score', input_data.get('assessment_score'))}/100
- Class Participation: {input_data.get('Participation_Score', input_data.get('participation_score'))}/100
- Sleep Hours: {input_data.get('Sleep_Hours', input_data.get('sleep_hours'))} hrs/night
- Tutoring Sessions: {input_data.get('Tutoring_Sessions', input_data.get('tutoring_sessions'))} sessions
- Extracurricular: {input_data.get('Extracurricular_Activities', input_data.get('extracurricular_activities'))}
- Internet Access: {input_data.get('Internet_Access', input_data.get('internet_access'))}

MACHINE LEARNING MODEL OUTPUT:
- Predicted Performance Class: {predicted_class}
- Model Confidence: {conf_display}
- Risk Classification: {risk_category} (Risk Score: {risk_score}%)
{consensus_section}
KEY CONTRIBUTING FACTORS (Explainable AI Attribution):
{factors_summary}

Respond ONLY with a valid JSON object matching the requested schema.
"""

def generate_grounded_fallback(
    student_name: str,
    predicted_class: str,
    risk_category: str,
    risk_score: float,
    input_data: Dict[str, Any],
    contributing_factors: List[Dict[str, Any]],
    consensus: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Deterministic, highly accurate, and grounded pedagogical rule engine fallback
    when no external LLM API key is provided or offline.
    """
    att = float(input_data.get('Attendance_Percentage', input_data.get('attendance_percentage', 75.0)))
    study = float(input_data.get('Study_Hours_Per_Week', input_data.get('study_hours_per_week', 15.0)))
    prev = float(input_data.get('Previous_Grade', input_data.get('previous_grade', 70.0)))
    assign = float(input_data.get('Assignment_Score', input_data.get('assignment_score', 70.0)))
    assess = float(input_data.get('Assessment_Score', input_data.get('assessment_score', 70.0)))
    sleep = float(input_data.get('Sleep_Hours', input_data.get('sleep_hours', 7.0)))

    possible_causes = []
    attention_areas = []
    recommendations = []
    interventions = []

    if att < 75.0:
        possible_causes.append(f"Low classroom attendance ({att}%), missing key lectures and conceptual discussions.")
        attention_areas.append("Class Attendance & Presence")
        recommendations.append(f"Aim to raise attendance above 85% by establishing a consistent morning schedule.")
        interventions.append(f"Schedule a check-in with {student_name} to identify attendance barriers and monitor bi-weekly logs.")

    if study < 12.0:
        possible_causes.append(f"Insufficient weekly self-study time ({study} hrs/week vs cohort benchmark of 16 hrs).")
        attention_areas.append("Structured Self-Study Time")
        recommendations.append(f"Gradually increase self-study by 30-45 minutes each weekday using focused 25-minute Pomodoro sessions.")

    if assess < 60.0:
        possible_causes.append(f"Low assessment and test examination scores ({assess}/100), reflecting exam difficulty or test anxiety.")
        attention_areas.append("Exam Preparation & Test Strategies")
        recommendations.append("Review previous test mistakes with course instructors and complete timed practice questions.")
        interventions.append("Offer targeted remedial quiz reviews or assign peer tutoring support.")

    if assign < 60.0:
        possible_causes.append(f"Poor assignment completion and homework scores ({assign}/100).")
        attention_areas.append("Continuous Assignment Submission")
        recommendations.append("Break large homework assignments into daily milestones to submit work before deadlines.")

    if sleep < 6.0:
        possible_causes.append(f"Suboptimal sleep duration ({sleep} hrs/night), potentially contributing to cognitive fatigue during class.")
        recommendations.append(f"Prioritize getting 7-8 hours of sleep per night to maximize memory consolidation.")

    # High performance protective factors
    if predicted_class == "High":
        explanation = f"{student_name} is projected for High Academic Performance ({risk_category}) with an outstanding profile. Strong metrics in {'attendance and coursework' if att >= 80 else 'consistent study habits'} reinforce strong academic resilience."
        if not possible_causes:
            possible_causes.append(f"Consistent academic discipline: {att}% attendance and {study} hours of dedicated weekly study.")
        if not attention_areas:
            attention_areas.append("Advanced Topic Enrichment & Leadership")
        recommendations.extend([
            "Maintain current high-yield study routines while pursuing honors projects or peer mentoring.",
            "Explore advanced extracurricular competitions and research projects aligned with career interests."
        ])
        interventions.extend([
            "Recognize student achievements in department commendations.",
            "Encourage participation in academic leadership or peer-tutoring initiatives."
        ])
    elif predicted_class == "Low":
        explanation = f"{student_name} is currently identified as High Risk ({risk_score}% risk score) for poor academic performance. The machine learning model isolated significant challenges in {', '.join([c.get('feature_name_clean', '') for c in contributing_factors[:2]])}."
        if not attention_areas:
            attention_areas.append("Core Academic Competencies & Foundation")
        recommendations.append("Attend faculty office hours weekly to clarify difficult syllabus concepts before exams.")
        interventions.append("Initiate immediate academic counselor meeting to formulate an individualized remediation contract.")
    else: # Medium
        explanation = f"{student_name} is performing at a Moderate Risk level (Predicted: Satisfactory / Medium). While showing foundational stability, targeted effort in key lagging areas can elevate them to high academic distinction."
        if not attention_areas:
            attention_areas.append("Consistency in Exam & Assignment Execution")
        recommendations.append("Increase weekly study hours toward 18-20 hours and form collaborative study groups.")
        interventions.append("Monitor midterm progress and provide constructive feedback on upcoming major assignments.")

    # Integrate Model Consensus awareness into the natural language explanation
    if consensus:
        c_count = consensus.get("consensus_count", 0)
        c_pct = consensus.get("consensus_percentage", 0.0)
        c_status = consensus.get("consensus_status", "")
        c_final = consensus.get("final_prediction", risk_category)
        agreeing = consensus.get("agreeing_models", [])
        disagreeing = consensus.get("disagreeing_models", [])
        m_preds = consensus.get("model_predictions", {})
        avg_conf_disp = consensus.get("average_confidence_display", "Confidence unavailable")

        top_factors = [f.get("feature_name_clean", "") for f in contributing_factors[:2] if f.get("feature_name_clean")]
        factors_str = f"the student's {', '.join(top_factors)}" if top_factors else "academic performance and study-related features"

        if c_count == 3:
            consensus_lead = f"All three machine learning models ({', '.join(agreeing)}) agree that this student is at {c_final.lower()} (100% consensus, average confidence: {avg_conf_disp}). The strongest contributing factors are {factors_str}."
        elif c_count == 2:
            dis_info = f" (while {disagreeing[0]} projected {m_preds.get(disagreeing[0], {}).get('prediction', 'different risk')})" if disagreeing else ""
            consensus_lead = f"Two of the three machine learning models ({', '.join(agreeing)}) agree on a final prediction of {c_final} ({c_pct}% consensus{dis_info}, average confidence: {avg_conf_disp}). The strongest contributing factors are {factors_str}."
        else:
            consensus_lead = f"Machine learning models show divergence with no majority consensus ({c_status}). Individual model predictions: {', '.join([f'{m}: {p.get('prediction', 'Unknown')}' for m, p in m_preds.items()])}. The strongest contributing factors requiring attention are {factors_str}."

        explanation = f"{consensus_lead} {explanation}"

    return {
        "explanation": explanation,
        "possible_causes": possible_causes[:4] if possible_causes else ["Academic performance aligns closely with general class averages."],
        "attention_areas": attention_areas[:3] if attention_areas else ["Core Subject Mastery"],
        "personalized_recommendations": recommendations[:4],
        "early_interventions": interventions[:3] if interventions else ["Regular academic check-in at midterm."],
        "model_used": "Grounded-Pedagogical-Engine (Rule-Based Fallback)"
    }

async def generate_llm_explanation(
    student_id: str,
    student_name: str,
    input_data: Dict[str, Any],
    predicted_class: str,
    confidence: Optional[float],
    risk_category: str,
    risk_score: float,
    contributing_factors: List[Dict[str, Any]],
    consensus: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    api_key = os.getenv("LLM_API_KEY", settings.LLM_API_KEY).strip()
    provider = os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER).lower()
    model_name = os.getenv("LLM_MODEL", settings.LLM_MODEL)

    # If no API key provided, seamlessly use our pedagogical rule engine
    if not api_key and provider != "ollama":
        return generate_grounded_fallback(
            student_name=student_name,
            predicted_class=predicted_class,
            risk_category=risk_category,
            risk_score=risk_score,
            input_data=input_data,
            contributing_factors=contributing_factors,
            consensus=consensus
        )

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(
        student_id=student_id,
        student_name=student_name,
        input_data=input_data,
        predicted_class=predicted_class,
        confidence=confidence,
        risk_category=risk_category,
        risk_score=risk_score,
        contributing_factors=contributing_factors,
        consensus=consensus
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

        # 2. OpenAI / Compatible Provider
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

        # 3. Ollama Local Provider
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
        print(f"External LLM API call error: {e}. Falling back to grounded pedagogical engine.")

    # Graceful fallback if API call fails
    fallback = generate_grounded_fallback(
        student_name=student_name,
        predicted_class=predicted_class,
        risk_category=risk_category,
        risk_score=risk_score,
        input_data=input_data,
        contributing_factors=contributing_factors
    )
    fallback["model_used"] = f"Grounded Engine (API Fallback)"
    return fallback
