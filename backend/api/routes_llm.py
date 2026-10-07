from fastapi import APIRouter, HTTPException
from backend.models.schemas import LLMExplainRequest, LLMExplainResponse
from backend.llm.explanation import generate_llm_explanation
from backend.services.db_service import DatabaseService

router = APIRouter(prefix="/api/llm", tags=["LLM Explanation"])

@router.post("/explain", response_model=LLMExplainResponse)
async def explain_prediction(request: LLMExplainRequest):
    try:
        factors_dict = [f.model_dump() for f in request.contributing_factors]
        explanation_result = await generate_llm_explanation(
            student_id=request.student_id,
            student_name=request.student_name,
            input_data=request.input_data,
            predicted_class=request.predicted_class,
            confidence=request.confidence,
            risk_category=request.risk_category,
            risk_score=request.risk_score,
            contributing_factors=factors_dict,
            consensus=request.consensus
        )

        # Save recommendation to database
        rec_id = DatabaseService.save_recommendation({
            "student_id": request.student_id,
            "prediction_id": request.prediction_id,
            "explanation": explanation_result.get("explanation", ""),
            "possible_causes": explanation_result.get("possible_causes", []),
            "attention_areas": explanation_result.get("attention_areas", []),
            "personalized_recommendations": explanation_result.get("personalized_recommendations", []),
            "early_interventions": explanation_result.get("early_interventions", []),
            "model_used": explanation_result.get("model_used", "AI-Pedagogical-Engine")
        })

        return {
            "student_id": request.student_id,
            "student_name": request.student_name,
            "predicted_class": request.predicted_class,
            "risk_category": request.risk_category,
            "explanation": explanation_result.get("explanation", ""),
            "possible_causes": explanation_result.get("possible_causes", []),
            "attention_areas": explanation_result.get("attention_areas", []),
            "personalized_recommendations": explanation_result.get("personalized_recommendations", []),
            "early_interventions": explanation_result.get("early_interventions", []),
            "model_used": explanation_result.get("model_used", "AI-Pedagogical-Engine"),
            "saved_to_db": True if rec_id else False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM explanation error: {str(e)}")
