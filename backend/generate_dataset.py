import numpy as np
import pandas as pd
import os

np.random.seed(42)
n_samples = 1200

first_names = [
    'Akashraj', 'Priya', 'Rahul', 'Sneha', 'Arun', 'Kavitha', 'Vikram', 'Divya', 'Sanjay', 'Ananya',
    'Manoj', 'Deepa', 'Karthik', 'Swetha', 'Vijay', 'Pooja', 'Ramesh', 'Meena', 'Harish', 'Ritu',
    'Bharath', 'Enosh', 'Dayanithi', 'Gokul', 'Ajay', 'Sathish', 'Varun', 'Kishore', 'Tharun', 'Ashwin'
]
last_names = [
    'Sharma', 'Kumar', 'Patel', 'Reddy', 'Singh', 'Iyer', 'Nair', 'Verma', 'Gupta', 'Rao',
    'Subramanian', 'Murugan', 'Menon', 'Pillai', 'Deshmukh', 'Joshi', 'Chopra', 'Malhotra', 'Bose', 'Das'
]

student_ids = [f'STU{1001 + i}' for i in range(n_samples)]
names = [f'{np.random.choice(first_names)} {np.random.choice(last_names)}' for _ in range(n_samples)]

# Core Academic Predictors matching presentation specification
attendance = np.clip(np.random.normal(76, 14, n_samples), 45, 100).round(1)
study_hours = np.clip(np.random.normal(16, 7, n_samples), 2, 40).round(1)
previous_grade = np.clip(np.random.normal(72, 13, n_samples), 40, 99).round(1)
assignment_score = np.clip(0.4 * previous_grade + 0.3 * study_hours * 2 + np.random.normal(25, 8, n_samples), 35, 100).round(1)
assessment_score = np.clip(0.45 * previous_grade + 0.35 * attendance * 0.5 + 0.2 * assignment_score + np.random.normal(0, 7, n_samples), 30, 100).round(1)
participation_score = np.clip(0.6 * attendance + np.random.normal(20, 10, n_samples), 30, 100).round(1)
sleep_hours = np.clip(np.random.normal(7.0, 1.2, n_samples), 4.0, 10.0).round(1)
tutoring_sessions = np.random.choice([0, 1, 2, 3, 4, 5], size=n_samples, p=[0.45, 0.25, 0.15, 0.08, 0.05, 0.02])
extracurricular = np.random.choice(['Yes', 'No'], size=n_samples, p=[0.55, 0.45])
parental_education = np.random.choice(['High School', 'Bachelor', 'Master', 'Doctorate'], size=n_samples, p=[0.35, 0.45, 0.15, 0.05])
internet_access = np.random.choice(['Yes', 'No'], size=n_samples, p=[0.92, 0.08])

# Composite scoring for ground truth performance class
composite = (
    0.28 * attendance +
    0.25 * previous_grade +
    0.20 * assessment_score +
    0.15 * assignment_score +
    0.12 * (study_hours / 40.0 * 100) +
    0.05 * participation_score +
    0.03 * tutoring_sessions * 10 +
    (sleep_hours - 7.0) * 1.5 +
    (extracurricular == 'Yes').astype(float) * 2.0 +
    (internet_access == 'Yes').astype(float) * 3.0 +
    np.random.normal(0, 4.5, n_samples)
)

performance_class = []
for c in composite:
    if c >= 74.0:
        performance_class.append('High')
    elif c >= 58.0:
        performance_class.append('Medium')
    else:
        performance_class.append('Low')

df = pd.DataFrame({
    'Student_ID': student_ids,
    'Name': names,
    'Attendance_Percentage': attendance,
    'Study_Hours_Per_Week': study_hours,
    'Previous_Grade': previous_grade,
    'Assignment_Score': assignment_score,
    'Assessment_Score': assessment_score,
    'Participation_Score': participation_score,
    'Sleep_Hours': sleep_hours,
    'Tutoring_Sessions': tutoring_sessions,
    'Extracurricular_Activities': extracurricular,
    'Parental_Education': parental_education,
    'Internet_Access': internet_access,
    'Performance_Class': performance_class
})

os.makedirs('data/raw', exist_ok=True)
df.to_csv('data/raw/student_performance_data.csv', index=False)
print('Saved data/raw/student_performance_data.csv')
print('Shape:', df.shape)
print('Distribution:')
print(df['Performance_Class'].value_counts())

# Generate sample batch upload template with 30 students (without Target)
sample_batch = df.drop(columns=['Performance_Class']).head(30)
sample_batch.to_csv('data/raw/sample_upload_template.csv', index=False)
print('Saved data/raw/sample_upload_template.csv')
