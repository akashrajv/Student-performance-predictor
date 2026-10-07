import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root or backend
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
if not os.getenv("LLM_API_KEY"):
    load_dotenv(BASE_DIR / ".env.example")

class Settings:
    PROJECT_NAME: str = "Student Performance Predictor"
    VERSION: str = "1.0.0"
    AUTHOR: str = "Akashraj (61782324110006)"
    
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_PATH: Path = BASE_DIR / "data" / "raw" / "student_performance_data.csv"
    SAMPLE_TEMPLATE_PATH: Path = BASE_DIR / "data" / "raw" / "sample_upload_template.csv"
    RECRUITMENT_DATA_PATH: Path = BASE_DIR / "data" / "raw" / "recruitment_data.csv"
    ARTIFACTS_DIR: Path = BASE_DIR / "artifacts"
    DB_PATH: Path = BASE_DIR / "database.sqlite"
    
    # LLM Settings
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini") # auto, gemini, openai, ollama
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Risk Classification Thresholds
    # Low Performance prob >= 0.40 -> High Risk
    # Low Performance prob in [0.15, 0.40] or Medium prob >= 0.50 -> Moderate Risk
    # High Performance prob >= 0.60 -> Low Risk
    RISK_HIGH_THRESHOLD: float = 0.40
    RISK_MODERATE_THRESHOLD: float = 0.20

settings = Settings()

# Ensure required directories exist
settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "raw").mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)
