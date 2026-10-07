import numpy as np
import pandas as pd
from typing import Dict, Any, List
from backend.ml.preprocessing import PreprocessingPipeline

FRIENDLY_NAMES = {
    'Attendance_Percentage': 'Attendance Rate',
    'Previous_Semester_CGPA': 'Previous Semester CGPA',
    'Internal_Marks': 'Internal Assessment Marks',
    'Assignment_Score': 'Assignment Performance',
    'Quiz_Score': 'Quiz Score',
    'Study_Hours_Per_Day': 'Daily Study Hours',
    'Previous_Backlogs': 'Previous Backlogs Count',
    'Practical_Marks': 'Practical Lab Marks',
    'Study_Hours_Per_Week': 'Weekly Study Hours',
    'Previous_Grade': 'Previous Academic Grade',
    'Assessment_Score': 'Assessment & Exam Score',
    'Participation_Score': 'Classroom Participation',
    'Sleep_Hours': 'Sleep Hours / Night',
    'Tutoring_Sessions': 'Tutoring Sessions / Month',
    'Extracurricular_Activities': 'Extracurricular Participation',
    'Parental_Education': 'Parental Education Level',
    'Internet_Access': 'High-Speed Internet Access'
}

UNITS = {
    'Attendance_Percentage': '%',
    'Previous_Semester_CGPA': ' / 10',
    'Internal_Marks': ' / 100',
    'Assignment_Score': ' / 100',
    'Quiz_Score': ' / 100',
    'Study_Hours_Per_Day': ' hrs/day',
    'Previous_Backlogs': ' backlogs',
    'Practical_Marks': ' / 100',
    'Study_Hours_Per_Week': ' hrs/week',
    'Previous_Grade': ' / 100',
    'Assessment_Score': ' / 100',
    'Participation_Score': ' / 100',
    'Sleep_Hours': ' hrs/night',
    'Tutoring_Sessions': ' sessions'
}

def explain_individual_prediction(
    student_dict: Dict[str, Any],
    pipeline: PreprocessingPipeline,
    model_name: str,
    feature_importances: Dict[str, float],
    predicted_class: str
) -> List[Dict[str, Any]]:
    """
    Computes local feature contribution and attribution for an individual student
    relative to cohort benchmark statistics.
    """
    contributions = []
    stats = pipeline.feature_stats

    for feat in pipeline.numerical_cols:
        val = student_dict.get(feat)
        if val is None:
            # Check lowercase/underscore variants
            for k in student_dict:
                if k.lower().replace("_", "") == feat.lower().replace("_", ""):
                    val = student_dict[k]
                    break
        if val is None:
            continue
            
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            continue

        feat_stat = stats.get(feat, {"mean": 50.0, "std": 15.0})
        mean = feat_stat["mean"]
        std = feat_stat["std"] if feat_stat["std"] > 0 else 1.0

        is_inverted = 'backlog' in feat.lower()
        # Standardized z-score
        z = (val_float - mean) / std
        if is_inverted:
            z = -z

        # Weight by feature importance
        weight = feature_importances.get(feat, 0.1)
        contribution_score = round(float(z * weight * 10.0), 3)

        friendly = FRIENDLY_NAMES.get(feat, feat.replace("_", " "))
        unit = UNITS.get(feat, "")
        diff = round(val_float - mean, 2)

        is_at_risk = predicted_class in ["Poor", "Low"]
        is_top = predicted_class in ["Excellent", "High"]

        if is_at_risk:
            # For backlogs, positive difference is negative
            is_worse = diff > 0.5 if is_inverted else diff < -1.5
            is_better = diff < -0.5 if is_inverted else diff > 1.5
            if is_worse:
                impact = "Negative"
                desc = f"{friendly} of {val_float}{unit} is below cohort benchmark ({round(mean, 1)}{unit}), increasing academic risk."
            elif is_better:
                impact = "Positive"
                desc = f"{friendly} of {val_float}{unit} is better than cohort benchmark ({round(mean, 1)}{unit}), acting as a protective factor."
            else:
                impact = "Neutral"
                desc = f"{friendly} of {val_float}{unit} is close to cohort benchmark ({round(mean, 1)}{unit})."
        elif is_top:
            is_better = diff < -0.5 if is_inverted else diff > 1.5
            is_worse = diff > 0.5 if is_inverted else diff < -1.5
            if is_better:
                impact = "Positive"
                desc = f"{friendly} of {val_float}{unit} exceeds cohort average ({round(mean, 1)}{unit}), driving strong academic distinction."
            elif is_worse:
                impact = "Negative"
                desc = f"{friendly} of {val_float}{unit} is below cohort average ({round(mean, 1)}{unit}), representing room for further enhancement."
            else:
                impact = "Neutral"
                desc = f"{friendly} of {val_float}{unit} is on par with cohort benchmark ({round(mean, 1)}{unit})."
        else: # Average / Good / Medium
            is_better = diff < -0.5 if is_inverted else diff > 2.0
            is_worse = diff > 0.5 if is_inverted else diff < -2.0
            if is_better:
                impact = "Positive"
                desc = f"{friendly} of {val_float}{unit} is a notable strength above cohort benchmark ({round(mean, 1)}{unit})."
            elif is_worse:
                impact = "Negative"
                desc = f"{friendly} of {val_float}{unit} is below cohort average ({round(mean, 1)}{unit}), holding back overall performance."
            else:
                impact = "Neutral"
                desc = f"{friendly} of {val_float}{unit} aligns with cohort average ({round(mean, 1)}{unit})."

        contributions.append({
            "feature": feat,
            "feature_name_clean": friendly,
            "value": f"{val_float}{unit}",
            "raw_value": val_float,
            "benchmark": f"{round(mean, 1)}{unit}",
            "difference": diff,
            "impact": impact,
            "contribution_score": contribution_score,
            "description": desc
        })

    # Sort so that for at-risk class, most negative factors come first; for top, most positive come first
    if predicted_class in ["Poor", "Low"]:
        contributions.sort(key=lambda x: x["contribution_score"])
    else:
        contributions.sort(key=lambda x: x["contribution_score"], reverse=True)

    return contributions
