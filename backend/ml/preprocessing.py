import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from typing import Tuple, Dict, Any, List
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from backend.config import settings

TARGET_COLS_DEFAULT = ['Performance_Level', 'Performance_Class', 'Target', 'Label']
ID_COLS = ['student_id', 'name', 'id', 'student_name']

class PreprocessingPipeline:
    def __init__(self):
        self.preprocessor = None
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.numerical_cols = []
        self.categorical_cols = []
        self.target_col = None
        self.feature_stats = {}  # Mean, std, median for explainability

    def fit(self, df: pd.DataFrame, target_col: str = None) -> 'PreprocessingPipeline':
        # 1. Determine target column
        if target_col and target_col in df.columns:
            self.target_col = target_col
        else:
            found_target = None
            for candidate in TARGET_COLS_DEFAULT:
                if candidate in df.columns:
                    found_target = candidate
                    break
            self.target_col = found_target if found_target else df.columns[-1]

        # 2. Determine ID columns to ignore
        id_cols_to_ignore = [
            c for c in df.columns 
            if c.lower() in ID_COLS or c.lower().endswith('_id') or c.lower() == 'id'
        ]

        # 3. Determine feature columns
        candidate_features = [
            c for c in df.columns 
            if c != self.target_col and c not in id_cols_to_ignore
        ]

        # Split into numerical and categorical
        self.numerical_cols = []
        self.categorical_cols = []
        for col in candidate_features:
            if pd.api.types.is_numeric_dtype(df[col]):
                self.numerical_cols.append(col)
            else:
                converted = pd.to_numeric(df[col], errors='coerce')
                if converted.notnull().sum() / max(len(df), 1) > 0.8:
                    self.numerical_cols.append(col)
                else:
                    self.categorical_cols.append(col)

        transformers = []
        if self.numerical_cols:
            num_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ])
            transformers.append(('num', num_pipeline, self.numerical_cols))

        if self.categorical_cols:
            cat_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ])
            transformers.append(('cat', cat_pipeline, self.categorical_cols))

        self.preprocessor = ColumnTransformer(transformers=transformers)
        
        X_df = df[self.numerical_cols + self.categorical_cols].copy()
        for col in self.numerical_cols:
            X_df[col] = pd.to_numeric(X_df[col], errors='coerce')
            
        self.preprocessor.fit(X_df)

        # Compute feature statistics (mean, std, min, max, median)
        for c in self.numerical_cols:
            series = pd.to_numeric(df[c], errors='coerce').dropna()
            self.feature_stats[c] = {
                "mean": float(series.mean()) if len(series) > 0 else 50.0,
                "std": float(series.std() if len(series) > 1 and series.std() > 0 else 1.0),
                "min": float(series.min()) if len(series) > 0 else 0.0,
                "max": float(series.max()) if len(series) > 0 else 100.0,
                "median": float(series.median()) if len(series) > 0 else 50.0
            }

        # Feature names
        num_names = list(self.numerical_cols)
        cat_names = []
        if 'cat' in self.preprocessor.named_transformers_:
            encoder = self.preprocessor.named_transformers_['cat'].named_steps['encoder']
            cat_names = list(encoder.get_feature_names_out(self.categorical_cols))

        self.feature_names = num_names + cat_names

        # Label encoder
        if self.target_col in df.columns:
            self.label_encoder.fit(df[self.target_col].astype(str))

        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if self.preprocessor is None:
            raise RuntimeError("Pipeline has not been fitted or loaded yet.")
            
        df_copy = df.copy()
        for col in self.numerical_cols:
            if col not in df_copy.columns:
                df_copy[col] = self.feature_stats.get(col, {}).get("median", 50.0)
            else:
                df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
                
        for col in self.categorical_cols:
            if col not in df_copy.columns:
                df_copy[col] = 'None'
                
        cols_to_transform = self.numerical_cols + self.categorical_cols
        return self.preprocessor.transform(df_copy[cols_to_transform])

    def transform_target(self, y: pd.Series) -> np.ndarray:
        return self.label_encoder.transform(y.astype(str))

    def inverse_transform_target(self, y_encoded: np.ndarray) -> np.ndarray:
        return self.label_encoder.inverse_transform(y_encoded)

    def save(self, filepath: Path = None):
        if filepath is None:
            filepath = settings.ARTIFACTS_DIR / "preprocessing.pkl"
        joblib.dump(self, filepath)
        
        # Save metadata JSON for frontend & debugging
        metadata = {
            "numerical_cols": self.numerical_cols,
            "categorical_cols": self.categorical_cols,
            "target_col": self.target_col,
            "classes": list(self.label_encoder.classes_) if hasattr(self.label_encoder, 'classes_') else [],
            "feature_names": self.feature_names,
            "feature_stats": self.feature_stats
        }
        with open(settings.ARTIFACTS_DIR / "feature_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def load(cls, filepath: Path = None) -> 'PreprocessingPipeline':
        if filepath is None:
            filepath = settings.ARTIFACTS_DIR / "preprocessing.pkl"
        if not filepath.exists():
            raise FileNotFoundError(f"Preprocessing pipeline file not found at {filepath}")
        return joblib.load(filepath)

