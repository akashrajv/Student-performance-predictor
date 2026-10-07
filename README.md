# 🎓 Student Performance Predictor (AI-Powered)

An enterprise-grade, end-to-end AI platform that predicts student academic performance using multiple machine learning architectures and leverages an LLM to generate transparent explanations, diagnose causes of underperformance, and provide personalized, actionable academic interventions.

> **Project Author:** Akashraj (61782324110006)  
> **Specification Reference:** *Student Performance Predictor* Project Presentation Specification  
> **Technology Stack:** React 19 • Vite • Tailwind CSS • Recharts • FastAPI • scikit-learn • XGBoost • SHAP • SQLite • LLM (Gemini / OpenAI / Ollama)

---

## 📌 1. Project Background & Objective

Traditional student prediction systems often rely on a single machine learning model and focus exclusively on scalar predictions without comparative benchmarking or explanation. As highlighted in the project presentation:
- Single models can suffer from bias, lack calibration, or fail to capture complex nonlinear dependencies.
- Black-box predictions fail to explain **why** a student is academically at risk.
- Without explainability, educators and academic counselors cannot intervene before exams occur.

### The Solution:
The **Student Performance Predictor** solves this challenge through:
1. **Multi-Model Machine Learning Pipeline:** Trains **Logistic Regression with L2 Regularization**, **Random Forest**, and **XGBoost** independently with the dataset, compares all models' accuracy scores (Training Accuracy and Test Accuracy), and automatically selects the one with the best training accuracy (no ensemble model used).
2. **Explainable AI (XAI):** Quantifies local feature contributions and cohort benchmark deviations to pinpoint specific risk drivers (e.g., low attendance, poor assessment scores, insufficient study hours).
3. **Grounded LLM Layer:** Translates model outputs into clear, empathetic, and actionable reports for teachers, academic advisors, and students.

---

## 🚀 2. System Architecture

```
Student Performance Predictor
│
├── frontend/                     # Modern React + Vite Web Application
│   ├── src/
│   │   ├── components/           # Reusable UI (Sidebar, Header, RiskBadge, FactorBreakdown, LLMCard)
│   │   ├── pages/                # Dashboard, PredictPage, BatchPage, ModelAnalysis, StudentDetails, DatasetTraining
│   │   ├── charts/               # Recharts components (Comparison, Confusion Matrix, Feature Importance, Risk Pie)
│   │   ├── services/             # Axios/Fetch API client layer
│   │   ├── App.jsx               # Navigation & application shell
│   │   └── index.css             # Tailwind design system & animations
│   ├── vite.config.js            # Vite build & API proxy setup
│   └── package.json
│
├── backend/                      # Production FastAPI Application
│   ├── main.py                   # ASGI application entry & router assembly
│   ├── config.py                 # Pydantic & environment settings
│   ├── api/                      # REST API route handlers
│   │   ├── routes_predict.py     # /api/predict & /api/batch-predict
│   │   ├── routes_models.py      # /api/models & /api/model-metrics
│   │   ├── routes_students.py    # /api/students & /api/student/{id}
│   │   ├── routes_llm.py         # /api/llm/explain
│   │   ├── routes_dashboard.py   # /api/dashboard/stats
│   │   └── routes_train.py       # /api/train & dataset management
│   ├── models/schemas.py         # Strict Pydantic request/response schemas
│   ├── services/db_service.py    # SQLite CRUD operations
│   ├── database/db.py            # SQLite schema initialization
│   ├── ml/                       # Machine Learning core
│   │   ├── preprocessing.py      # ColumnTransformer, Imputation & Scaling pipeline
│   │   ├── train.py              # Stratified split, training, evaluation, persistence
│   │   ├── predict.py            # Calibrated inference engine
│   │   ├── evaluate.py           # Classification metrics & confusion matrix
│   │   └── explain.py            # Local feature attribution & XAI engine
│   └── llm/
│       └── explanation.py        # Multi-provider LLM & pedagogical engine
│
├── data/
│   ├── raw/
│   │   ├── student_performance_data.csv  # 1,200 verified student records
│   │   └── sample_upload_template.csv    # Batch prediction template
│   └── processed/
│
├── artifacts/                    # Persisted serialized models & metadata
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── best_model.pkl            # Selected champion model based on training accuracy
│   ├── best_model_info.json      # Comparison scores & winner metadata
│   ├── preprocessing.pkl
│   ├── feature_metadata.json
│   └── model_metrics.json
│
├── tests/
│   └── test_ml_and_api.py        # Automated test suite (Pytest)
├── notebooks/                    # Jupyter Exploratory Data Analysis
├── .env.example                  # Environment configuration template
└── requirements.txt              # Python dependencies
```

---

## 🔬 3. Machine Learning Models & Empirical Results

All models are trained independently with a stratified 80/20 train/test split on 1,200 student records with 12 features. The system calculates and compares Training Accuracy against held-out Test Accuracy (240 unseen students), and designates the model with the highest training accuracy as the selected best model:

| Model Architecture | Training Accuracy | Test Accuracy | Precision | Recall | F1-Score | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **XGBoost Classifier** | **95.83%** | 76.25% | 76.25% | 76.25% | 75.93% | 0.908 | ★ **Selected Best Model** |
| **Random Forest** | **93.65%** | 76.67% | 78.69% | 76.67% | 74.66% | 0.899 | Candidate |
| **Logistic Regression (L2)** | **78.54%** | 80.83% | 80.92% | 80.83% | 80.65% | 0.932 | Candidate |

### Evaluated Student Predictors:
1. `Attendance_Percentage` (45% - 100%)
2. `Study_Hours_Per_Week` (2 - 40 hours)
3. `Previous_Grade` (Scaled grade 40 - 100)
4. `Assignment_Score` (Continuous assignment score 35 - 100)
5. `Assessment_Score` (Midterm and quiz examinations 30 - 100)
6. `Participation_Score` (Class engagement index 30 - 100)
7. `Sleep_Hours` (Nightly sleep 4 - 10 hours)
8. `Tutoring_Sessions` (Monthly tutoring support 0 - 5)
9. `Extracurricular_Activities` (Yes / No)
10. `Parental_Education` (High School / Bachelor / Master / Doctorate)
11. `Internet_Access` (Yes / No)
12. **Target (`Performance_Class`):** `High` (Good / Low Risk), `Medium` (Satisfactory / Moderate Risk), `Low` (Poor / High Risk)

---

## 🔍 4. Explainable AI & Risk Classification

### Academic Risk Formula:
The system derives the Risk Score directly from the calibrated model probability output:
$$\text{Risk Score (\%)} = \left( P(\text{Low}) \times 1.0 + P(\text{Medium}) \times 0.40 + P(\text{High}) \times 0.0 \right) \times 100$$

- **High Risk (Red):** $P(\text{Low}) \ge 0.40$ or Risk Score $\ge 50\%$
- **Moderate Risk (Amber):** $P(\text{Medium}) \ge 0.45$ or Risk Score $\in [25\%, 50\%)$
- **Low Risk (Green):** $P(\text{High}) \ge 0.60$ and Risk Score $< 25\%$

### Local Feature Contribution Engine:
For each feature $i$, the standardized deviation from cohort average is scaled by global model importance weight:
$$c_i = \left( \frac{x_i - \mu_i}{\sigma_i} \right) \times w_i$$
Features falling significantly below cohort averages are isolated as **Negative Risk Drivers**, showing exactly why the student is projected to struggle.

---

## 🤖 5. Grounded LLM Layer

The LLM receives strictly verified model outputs and generates:
1. **Natural Language Explanation:** 2-3 sentences explaining the outcome in non-technical terms.
2. **Possible Causes:** Grounded strictly in the student's metrics (e.g., attendance < 75%, study < 12 hrs).
3. **Areas Needing Attention:** Focused subject areas and study habits.
4. **Personalized Recommendations:** Actionable study strategies (Pomodoro routines, assignment milestones).
5. **Early Interventions for Educators:** Check-in meetings, tutoring referrals, and remedial progress checks.

> **Reliability Guarantee:** If no external LLM API key is configured or the network is offline, the integrated deterministic **Pedagogical Rule Engine** automatically formats the structured report without errors.

---

## ⚡ 6. Quick Start & Execution

### Prerequisites:
- Python 3.10+ (Python 3.14 compatible)
- Node.js 18+ and npm

### Step 1: Clone and Setup Python Environment
```bash
git clone <repo-url>
cd "Student Performance Predictor"

# Create and activate virtual environment
python -m venv backend/venv

# Windows Powershell:
.\backend\venv\Scripts\Activate.ps1

# Linux / macOS:
# source backend/venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### Step 2: Initialize Database and Train Models
```bash
python run_train.py
```
*This command validates data, trains all 4 models, evaluates metrics, saves artifacts, and seeds sample students into SQLite.*

### Step 3: Run the Test Suite
```bash
pytest tests/test_ml_and_api.py -v
```

### Step 4: Run the Dashboard

#### Option A: Streamlit Dashboard (Recommended / Presentation Spec)
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser for the full interactive Streamlit dashboard!

#### Option B: React + Vite + FastAPI Dashboard
In Terminal 1 (FastAPI Backend):
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
In Terminal 2 (React Frontend):
```bash
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** or **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

### Streamlit Application:
Alternatively, launch the complete interactive Streamlit portal:
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)**.

---

## 📄 7. AI Resume Analyzer & Placement Readiness Feature

A major module bridging academic intelligence with career readiness. Students upload their resume (PDF or DOCX) to receive deterministic skill gap analysis against campus recruitment datasets, empirical placement readiness scoring, and grounded AI career intervention roadmaps.

### End-to-End Workflow:
```
Resume Upload (PDF / DOCX)
        ↓
Reliable Text Extraction (pypdf / python-docx)
        ↓
Factual Information & Skill Extraction (Categorized Taxonomy)
        ↓
Recruitment Dataset Analysis (Source of Truth with Dynamic Schema Detection)
        ↓
Deterministic Skill Matching (Matched / Partial / Missing)
        ↓
Skill Priority Analysis (High / Medium / Low from Empirical Dataset Frequencies)
        ↓
Company & Role Alignment (Company-by-Company Eligibility & Coverage)
        ↓
Placement Readiness Evaluation (Project-defined Placement Readiness Score 0-100%)
        ↓
Existing Grounded LLM Layer (Gemini / OpenAI / Ollama / Grounded Fallback)
        ↓
Personalized Placement Improvement Plan (Actionable, Timeline-Sequenced Cards)
```

### Key Technical Pillars:
1. **Multi-Format Resume Text Extraction:** Handles PDF (`pypdf`) and Word (`python-docx`) files with input validation for empty documents, corrupted files, unsupported formats, and insufficient readable text.
2. **Deterministic Skill Matching Engine:** Case-insensitive normalization, synonym/alias expansion, and related skill family mapping (e.g. Scikit-learn → Machine Learning foundation) while strictly guarding against false positives (e.g., Java ≠ JavaScript).
3. **Dynamic Schema Discovery:** Source-of-truth recruitment dataset loader dynamically discovers company, role, CGPA cutoff, required skills, preferred skills, and eligibility columns without hardcoding.
4. **Empirical Skill Demand Prioritization:** Calculates exact requirement frequencies across all recruitment records; categorizes missing skills into High (≥30%), Medium (15-29%), and Low (<15%) priority tiers without invented numbers.
5. **Project-Defined Placement Readiness Score:** Transparent composite index (0–100%) factoring in Core Requirement Coverage (45%), Market Demand Adoption (20%), Practical Portfolio Projects (15%), Industry Experience (10%), and Academic Baseline (10%). Clearly labeled as an educational guidance indicator.
6. **Existing LLM Reuse:** Reuses the established multi-provider LLM infrastructure (Google Gemini, OpenAI, Ollama) and includes a deterministic grounded fallback engine for offline reliability.

---

## 📡 8. REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/predict` | Predict individual student performance, compute risk, save record |
| `POST` | `/api/predict-consensus` | Evaluate all 3 models (LR, RF, XGBoost) and compute Model Consensus |
| `POST` | `/api/batch-predict` | Upload cohort CSV for batch scoring and distribution analytics |
| `GET` | `/api/models` | List available model architectures and descriptions |
| `GET` | `/api/model-metrics` | Retrieve Accuracy, Precision, Recall, F1, Confusion Matrix, and ROC-AUC |
| `GET` | `/api/students` | Search and list students with pagination |
| `GET` | `/api/student/{id}` | Get complete 360° student profile and historical predictions |
| `POST` | `/api/llm/explain` | Generate grounded LLM explanation and personalized action plan |
| `POST` | `/api/resume/analyze` | Upload PDF/DOCX resume for deterministic matching & placement readiness |
| `GET` | `/api/resume/recruitment-market` | Retrieve recruitment companies, roles, and empirical skill demand tiers |
| `GET` | `/api/resume/history` | List historical resume analyses saved in SQLite |
| `GET` | `/api/resume/{id}` | Get detailed report for a past resume analysis |
| `GET` | `/api/resume/student/{id}/profile`| Connect student academic prediction with latest resume profile |
| `GET` | `/api/dashboard/stats`| High-level KPIs, model accuracy comparison, and risk counts |
| `POST` | `/api/train` | Retrain all ML models on active dataset |
| `POST` | `/api/dataset/upload`| Upload custom CSV dataset and retrain pipeline |
| `GET` | `/api/dataset/sample`| Download sample CSV batch prediction template |
| `GET` | `/api/health` | Health check and trained artifact readiness |

---

## 🧪 9. Automated Test Coverage (34/34 Passing)

The test suite validates:
- [x] **TEST 1:** Upload valid PDF resume with automated text extraction
- [x] **TEST 2:** Upload valid DOCX resume with paragraph & table parsing
- [x] **TEST 3:** Resume containing many matching skills (≥85% score)
- [x] **TEST 4:** Resume containing several missing skills (isolated gaps)
- [x] **TEST 5:** Company-wise matching across verified recruitment records
- [x] **TEST 6:** Empirical skill priority calculation from dataset frequencies
- [x] **TEST 7:** LLM recommendations schema compliance and realism
- [x] **TEST 8:** Invalid file upload rejection (unsupported formats & corrupt data)
- [x] **TEST 9:** Empty resume document validation (0-byte handling)
- [x] **TEST 10:** Missing recruitment dataset graceful handling
- [x] **TEST 11:** LLM/API failure fallback to grounded deterministic engine
- [x] **TEST 12:** Existing Student Performance Predictor regression verification
- [x] **TEST 13:** Model Consensus multi-model agreement verification
- [x] **TEST 14:** Explainable AI feature attribution regression verification
