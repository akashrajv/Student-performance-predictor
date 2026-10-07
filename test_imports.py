import sys
print("Python version:", sys.version)

print("Importing os, json, sqlite3...")
import os, json, sqlite3
print("OK")

print("Importing numpy, pandas...")
import numpy as np
import pandas as pd
print("OK")

print("Importing sklearn...")
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score
print("sklearn OK")

print("Importing xgboost...")
import xgboost
from xgboost import XGBClassifier
print("xgboost OK:", xgboost.__version__)

print("All imports tested successfully!")
