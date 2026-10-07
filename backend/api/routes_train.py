import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from backend.config import settings
from backend.ml.train import train_all_models
from backend.ml.predict import PredictionEngine
import pandas as pd

router = APIRouter(prefix="/api", tags=["Training & Dataset"])

@router.post("/train")
async def trigger_training():
    try:
        res = train_all_models(str(settings.RAW_DATA_PATH))
        # Invalidate in-memory cached model artifacts so new models take effect
        PredictionEngine.reload_artifacts()
        return {
            "status": "success",
            "message": f"All 3 models independently trained. Selected Best Model: {res['best_model']} (Train Accuracy: {res['best_training_accuracy'] * 100:.2f}%).",
            "best_model": res["best_model"],
            "best_training_accuracy": res["best_training_accuracy"],
            "comparison": res["comparison"],
            "dataset_records": res["dataset_records"],
            "train_size": res["train_size"],
            "test_size": res["test_size"],
            "models_evaluated": res["models_evaluated"],
            "metrics": res["metrics"],
            "trained_at": res["trained_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@router.post("/dataset/upload")
async def upload_training_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV dataset files are supported.")
        
    try:
        dest_path = settings.DATA_DIR / "raw" / "uploaded_dataset.csv"
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df = pd.read_csv(dest_path)
        if len(df) < 20:
            raise HTTPException(status_code=400, detail="Dataset must contain at least 20 records for train/test split.")

        # Train models with uploaded dataset
        res = train_all_models(str(dest_path))
        PredictionEngine.reload_artifacts()

        return {
            "status": "success",
            "message": f"Successfully loaded dataset with {len(df)} rows. Selected Best Model: {res['best_model']} (Train Accuracy: {res['best_training_accuracy'] * 100:.2f}%).",
            "dataset_shape": df.shape,
            "columns": list(df.columns),
            "best_model": res["best_model"],
            "best_training_accuracy": res["best_training_accuracy"],
            "comparison": res["comparison"],
            "metrics": res["metrics"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset processing error: {str(e)}")

@router.get("/dataset/sample")
async def download_sample_template():
    if not settings.SAMPLE_TEMPLATE_PATH.exists():
        raise HTTPException(status_code=404, detail="Sample template not found.")
    return FileResponse(
        path=str(settings.SAMPLE_TEMPLATE_PATH),
        filename="student_performance_sample_template.csv",
        media_type="text/csv"
    )

@router.get("/dataset/preview")
async def preview_dataset():
    if not settings.RAW_DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df = pd.read_csv(settings.RAW_DATA_PATH)
    return {
        "total_records": len(df),
        "columns": list(df.columns),
        "preview": df.head(10).to_dict(orient="records")
    }
