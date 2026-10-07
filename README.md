Student Performance Portal – AI-Powered Student & Placement Analytics
Monitor academic performance, understand student risk factors, and prepare for placements with an intelligent student performance and career guidance platform.
Features
Student Performance Prediction
- Predicts student academic performance using machine learning
- Uses Logistic Regression, Random Forest, and XGBoost
- Analyses factors such as attendance, previous marks, assessments, assignments, and other academic attributes
Model Consensus
- Compares predictions from multiple machine learning models
- Shows whether the models agree on the prediction
- Provides:
  - Strong Consensus – 3/3 models agree
  - Moderate Consensus – 2/3 models agree
  - Model Disagreement – no clear majority
Explainable AI
- Explains why a student received a particular prediction
- Identifies important factors influencing the result
- Helps students and faculty understand the prediction instead of viewing it as a black-box result
AI-Powered Recommendations
- Uses the existing LLM integration to convert model results into simple explanations
- Provides personalized suggestions for improving academic performance
- Separates ML prediction from LLM-based explanation
Resume Analyzer
- Upload resumes in PDF/DOCX format
- Extracts:
  - Education
  - Programming languages
  - Technical skills
  - Frameworks
  - Databases
  - Projects
  - Internships
  - Certifications
- Analyses the student's current technical profile
Recruitment Skill Gap Analysis
- Compares resume skills with the requirements in the recruitment dataset
- Identifies:
  - Matched Skills
  - Partially Matched Skills
  - Missing Skills
- Highlights important skills that students should improve
Company-Wise Matching
- Compares a student's resume against available company/job-role requirements
- Shows how closely the student's profile matches different recruitment opportunities
- Helps students focus their preparation on relevant companies and roles
Placement Readiness
- Provides a project-defined indication of placement preparation
- Considers skill matching, missing skills, projects, and recruitment requirements
- Helps students understand their current strengths and areas for improvement
Personalized Improvement Plan
- Generates recommendations based on identified academic and career gaps
- Suggests:
  - Skills to learn
  - Projects to build
  - Areas to improve
  - Resume improvements
  - Placement preparation activities
Student-Friendly Dashboard
- Clean and interactive interface
- Combines academic prediction and placement analysis
- Provides results in an easy-to-understand format
How It Works
Academic Performance Prediction
1. Student academic information is entered into the system
2. Data is validated and preprocessed
3. Three machine learning models analyse the student data:
   - Logistic Regression
   - Random Forest
   - XGBoost
4. Predictions from the models are compared
5. Model Consensus determines the level of agreement
6. Explainable AI identifies important factors
7. Existing LLM converts the results into understandable feedback
8. Personalized recommendations are generated
Resume Analysis
1. Student uploads a resume
2. Resume text is extracted from the PDF/DOCX file
3. Important resume information and skills are identified
4. Extracted skills are compared with the recruitment dataset
5. Skills are classified as:
   - Matched
   - Partially Matched
   - Missing
6. Relevant companies and job roles are identified
7. Placement readiness is calculated
8. Existing LLM generates personalized improvement suggestions
System Workflow
             STUDENT DATA
                  │
                  ▼
            PREPROCESSING
                  │
                  ▼
       ┌──────────┼──────────┐
       ▼          ▼          ▼
   Logistic   Random      XGBoost
  Regression  Forest
       │          │          │
       └──────────┼──────────┘
                  ▼
          MODEL CONSENSUS
                  │
                  ▼
          EXPLAINABLE AI
                  │
                  ▼
          EXISTING LLM
                  │
                  ▼
       ACADEMIC RECOMMENDATION


              RESUME
                │
                ▼
        TEXT EXTRACTION
                │
                ▼
      SKILL INFORMATION
         EXTRACTION
                │
                ▼
      RECRUITMENT DATASET
                │
                ▼
         SKILL MATCHING
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
    MATCHED   PARTIAL   MISSING
       │        │        │
       └────────┼────────┘
                ▼
       COMPANY/ROLE MATCH
                │
                ▼
       PLACEMENT READINESS
                │
                ▼
          EXISTING LLM
                │
                ▼
     PERSONALIZED IMPROVEMENT

Tech Stack
- Programming: Python
- Machine Learning: Scikit-learn, XGBoost
- ML Models: Logistic Regression, Random Forest, XGBoost
- Explainable AI: SHAP / Feature Importance
- LLM: Existing LLM integration used in the project
- Resume Processing: PDF / DOCX text extraction
- Data Processing: Pandas, NumPy
- Frontend: Streamlit / Existing project UI
- Data Storage: Existing project dataset/storage
- Visualization: Existing dashboard visualization components
Machine Learning Models
Logistic Regression
Used as a baseline classification model with L2 regularization.
Random Forest
Uses multiple decision trees to improve prediction stability and handle different student-related features.
XGBoost
Uses gradient boosting to build a strong predictive model by learning from errors made by previous trees.
The predictions from all three models can be compared using the Model Consensus feature.
Explainable AI
The system does not simply provide a prediction.
For example:
Prediction: High Risk

Important Factors:
✓ Low Attendance
✓ Low Previous Marks
✓ Poor Assessment Score
✓ Low Assignment Performance

These factors are then provided to the existing LLM so that the result can be explained in simple language.
Resume Skill Gap Analysis
Example:
Resume Skills:
Python
Java
SQL
React

Recruitment Requirements:
Python
SQL
Machine Learning
Docker
AWS

The system can produce:
✓ Matched:
Python
SQL

⚠ Partially Matched:
React / related technologies

✗ Missing:
Machine Learning
Docker
AWS

The missing skills can then be prioritized based on their frequency in the recruitment dataset.
Placement Readiness
The system provides a project-defined placement readiness indicator based on the available recruitment information.
Example:
Technical Skills      : Good
Programming Skills    : Good
Projects              : Moderate
Recruitment Matching  : Moderate
Resume Alignment      : Good

Overall Readiness     : Moderate

Note: Placement Readiness is a guidance indicator created for this project and does not represent a guaranteed probability of placement.

Example Use Case
Academic Prediction
Input:
Attendance: 68%
Previous Marks: 62%
Assignment Score: 65%
Assessment Score: 58%

Output:
Prediction: High Risk

Model Consensus:
2/3 Models → High Risk

Main Factors:
- Low Attendance
- Low Assessment Score
- Previous Academic Performance

The LLM then provides understandable suggestions for improving the student's academic performance.
Resume Analysis
Input:
Resume: Student_Resume.pdf
Target: Software Development Roles

Output:
Matched Skills:
✓ Java
✓ Python
✓ SQL

Missing Skills:
✗ Docker
✗ Cloud
✗ System Design

Placement Readiness:
Moderate

Priority:
1. Improve Docker knowledge
2. Learn cloud fundamentals
3. Strengthen software development projects

Key Advantages
- Combines academic prediction and placement preparation
- Uses multiple ML models instead of depending on a single model
- Provides model consensus
- Makes predictions explainable
- Uses LLM for understandable recommendations
- Automatically identifies resume skill gaps
- Compares resumes with actual recruitment data
- Provides company/job-role-specific analysis
- Helps students create a personalized improvement plan
- Supports data-driven academic and career decisions
Project Innovation
The main innovation of the project is the combination of academic intelligence and career intelligence in a single student platform.
Academic Performance
        +
Explainable AI
        +
LLM Assistance
        +
Resume Analysis
        +
Recruitment Data
        +
Skill Gap Analysis
        +
Placement Readiness

Instead of only predicting student performance, the system helps answer:
"How am I performing academically?"

"Why am I getting this prediction?"

"What should I improve?"

"What skills are missing from my resume?"

"Which recruitment requirements match my profile?"

"How can I prepare better for placements?"

Author
Akashraj V

Conclusion
The Student Performance Portal demonstrates how machine learning, Explainable AI, and Large Language Models can be combined to support students throughout their academic and placement journey.
The system goes beyond simple performance prediction by explaining the reasons behind predictions, providing personalized recommendations, analysing student resumes, identifying recruitment skill gaps, and providing placement-readiness guidance.
By bringing these capabilities together, the project provides a practical and intelligent platform that helps students understand their current performance, identify areas for improvement, and prepare more effectively for future placement opportunities.
