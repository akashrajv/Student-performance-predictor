from fastapi import APIRouter, HTTPException
from backend.services.db_service import DatabaseService
from backend.ml.predict import PredictionEngine

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats():
    try:
        stats = DatabaseService.get_dashboard_statistics()
        
        # Add model accuracy comparison & best model info
        metrics = PredictionEngine.get_metrics()
        accuracies = {}
        for m_name, m_data in metrics.items():
            if "ensemble" not in m_name.lower():
                accuracies[m_name] = m_data.get("accuracy", 0.0)
            
        stats["model_accuracies"] = accuracies
        best_info = PredictionEngine.get_best_model_info()
        stats["best_model"] = best_info.get("best_model_name", "XGBoost")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")
