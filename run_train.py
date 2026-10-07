import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath("."))

from backend.database.db import init_db
from backend.ml.train import train_all_models

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Training models...")
    res = train_all_models()
    print("\nTraining complete! Evaluated models:", res["models_evaluated"])
    print(f"[*] Selected Best Model by Training Accuracy: {res['best_model']} ({res['best_training_accuracy'] * 100:.2f}%)")
    print("\nModel Accuracy Comparison:")
    for comp in res["comparison"]:
        print(f"[{comp['model_name']}] Train Acc: {comp['train_accuracy'] * 100:.2f}% | Test Acc: {comp['test_accuracy'] * 100:.2f}% | F1: {comp['f1_score'] * 100:.2f}% {'[BEST SELECTED]' if comp['is_best'] else ''}")
