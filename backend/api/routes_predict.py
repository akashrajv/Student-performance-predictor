import io
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from backend.models.schemas import PredictRequest, PredictResponse, BatchPredictResponse
from backend.ml.predict import PredictionEngine
from backend.services.db_service import DatabaseService

router = APIRouter(prefix="/api", tags=["Prediction"])

@router.post("/predict", response_model=PredictResponse)
async def predict_student(request: PredictRequest):
    try:
        student_dict = request.student.model_dump()
        result = PredictionEngine.predict_single(student_dict, model_name=request.model_name)
        
        # Attach consensus if not already attached
        if "consensus" not in result or result["consensus"] is None:
            try:
                consensus_data = PredictionEngine.predict_consensus(student_dict)
                result["consensus"] = consensus_data.get("consensus")
            except Exception:
                result["consensus"] = None

        # Save or update student in DB
        DatabaseService.save_or_update_student(student_dict)
        
        # Save prediction in DB
        pred_id = DatabaseService.save_prediction({
            "student_id": result["student_id"],
            "student_name": result["student_name"],
            "model_used": result["model_used"],
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "risk_category": result["risk_category"],
            "risk_score": result["risk_score"],
            "probabilities": result["probabilities"],
            "contributing_factors": result["contributing_factors"],
            "input_data": result["input_data"]
        })
        result["prediction_id"] = pred_id
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/predict-consensus", response_model=PredictResponse)
async def predict_student_consensus(request: PredictRequest):
    try:
        student_dict = request.student.model_dump()
        result = PredictionEngine.predict_consensus(student_dict)
        
        # Save or update student in DB
        DatabaseService.save_or_update_student(student_dict)
        
        # Save prediction in DB
        pred_id = DatabaseService.save_prediction({
            "student_id": result["student_id"],
            "student_name": result["student_name"],
            "model_used": result["model_used"],
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "risk_category": result["risk_category"],
            "risk_score": result["risk_score"],
            "probabilities": result["probabilities"],
            "contributing_factors": result["contributing_factors"],
            "input_data": result["input_data"]
        })
        result["prediction_id"] = pred_id
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/batch-predict")
async def batch_predict_csv(
    file: UploadFile = File(...),
    model_name: Optional[str] = Form("XGBoost")
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
        
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")
        if len(df) > 5000:
            raise HTTPException(status_code=400, detail="Upload limit exceeded (max 5,000 students per batch).")

        predictions = []
        risk_counts = {"Low Risk": 0, "Moderate Risk": 0, "High Risk": 0, "Prediction Uncertain": 0}
        perf_counts = {"High": 0, "Medium": 0, "Low": 0, "Poor": 0, "Average": 0, "Good": 0, "Excellent": 0}
        students_to_save = []

        is_consensus_mode = bool(model_name and model_name.strip().lower() in ["model consensus", "consensus", "majority voting"])

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            # Generate default Student_ID if missing
            if 'Student_ID' not in row_dict and 'student_id' not in row_dict:
                row_dict['student_id'] = f"BATCH-{idx+1:04d}"
            if 'Name' not in row_dict and 'name' not in row_dict:
                row_dict['name'] = f"Student {idx+1}"

            if is_consensus_mode:
                pred_res = PredictionEngine.predict_consensus(row_dict)
            else:
                pred_res = PredictionEngine.predict_single(row_dict, model_name=model_name)
                # Compute consensus for full cohort analytics
                try:
                    c_data = PredictionEngine.predict_consensus(row_dict)
                    pred_res["consensus"] = c_data.get("consensus")
                except Exception:
                    pred_res["consensus"] = None
            
            # Count distributions
            risk_cat = pred_res.get("risk_category", "Unknown")
            risk_counts[risk_cat] = risk_counts.get(risk_cat, 0) + 1
            pred_cls = pred_res.get("predicted_class", "Unknown")
            perf_counts[pred_cls] = perf_counts.get(pred_cls, 0) + 1

            students_to_save.append(row_dict)
            predictions.append(pred_res)

        # Batch save students to database
        DatabaseService.save_students_batch(students_to_save)

        return {
            "total_students": len(predictions),
            "model_used": model_name,
            "risk_distribution": risk_counts,
            "performance_distribution": perf_counts,
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

