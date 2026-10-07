import json
from typing import List, Dict, Any, Optional
from backend.database.db import get_connection

class DatabaseService:
    @staticmethod
    def _extract_student_tuple(s: Dict[str, Any]) -> tuple:
        s_id = str(s.get("Student_ID") or s.get("student_id") or "STU-UNKNOWN")
        name = str(s.get("Name") or s.get("name") or s_id)
        att = float(s.get("Attendance_Percentage") or s.get("attendance_percentage") or 75.0)

        study_w = s.get("Study_Hours_Per_Week") or s.get("study_hours_per_week")
        if study_w is None:
            study_d = s.get("Study_Hours_Per_Day") or s.get("study_hours_per_day") or 2.0
            study_w = float(study_d) * 7.0
        else:
            study_w = float(study_w)

        prev_g = s.get("Previous_Grade") or s.get("previous_grade")
        if prev_g is None:
            cgpa = s.get("Previous_Semester_CGPA") or s.get("previous_semester_cgpa") or 7.0
            prev_g = float(cgpa) * 10.0
        else:
            prev_g = float(prev_g)

        assign = float(s.get("Assignment_Score") or s.get("assignment_score") or 70.0)

        assess = s.get("Assessment_Score") or s.get("assessment_score")
        if assess is None:
            assess = s.get("Internal_Marks") or s.get("internal_marks") or 70.0
        assess = float(assess)

        part = s.get("Participation_Score") or s.get("participation_score")
        if part is None:
            part = s.get("Quiz_Score") or s.get("quiz_score") or 70.0
        part = float(part)

        sleep = float(s.get("Sleep_Hours") or s.get("sleep_hours") or 7.0)

        tutor = s.get("Tutoring_Sessions") or s.get("tutoring_sessions")
        if tutor is None:
            tutor = s.get("Previous_Backlogs") or s.get("previous_backlogs") or 0
        tutor = int(tutor)

        extra = str(s.get("Extracurricular_Activities") or s.get("extracurricular_activities") or "No")
        parent_ed = str(s.get("Parental_Education") or s.get("parental_education") or "Bachelor")
        net = str(s.get("Internet_Access") or s.get("internet_access") or "Yes")

        return (s_id, name, att, study_w, prev_g, assign, assess, part, sleep, tutor, extra, parent_ed, net)

    @staticmethod
    def save_or_update_student(student_data: Dict[str, Any]) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO students (
                student_id, name, attendance_percentage, study_hours_per_week,
                previous_grade, assignment_score, assessment_score,
                participation_score, sleep_hours, tutoring_sessions,
                extracurricular_activities, parental_education, internet_access
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                name=excluded.name,
                attendance_percentage=excluded.attendance_percentage,
                study_hours_per_week=excluded.study_hours_per_week,
                previous_grade=excluded.previous_grade,
                assignment_score=excluded.assignment_score,
                assessment_score=excluded.assessment_score,
                participation_score=excluded.participation_score,
                sleep_hours=excluded.sleep_hours,
                tutoring_sessions=excluded.tutoring_sessions,
                extracurricular_activities=excluded.extracurricular_activities,
                parental_education=excluded.parental_education,
                internet_access=excluded.internet_access
        """, DatabaseService._extract_student_tuple(student_data))
        
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    @staticmethod
    def save_students_batch(students_list: List[Dict[str, Any]]):
        if not students_list:
            return
        conn = get_connection()
        cursor = conn.cursor()
        
        rows = [DatabaseService._extract_student_tuple(s) for s in students_list]
            
        cursor.executemany("""
            INSERT INTO students (
                student_id, name, attendance_percentage, study_hours_per_week,
                previous_grade, assignment_score, assessment_score,
                participation_score, sleep_hours, tutoring_sessions,
                extracurricular_activities, parental_education, internet_access
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                name=excluded.name,
                attendance_percentage=excluded.attendance_percentage,
                study_hours_per_week=excluded.study_hours_per_week,
                previous_grade=excluded.previous_grade,
                assignment_score=excluded.assignment_score,
                assessment_score=excluded.assessment_score,
                participation_score=excluded.participation_score,
                sleep_hours=excluded.sleep_hours,
                tutoring_sessions=excluded.tutoring_sessions,
                extracurricular_activities=excluded.extracurricular_activities,
                parental_education=excluded.parental_education,
                internet_access=excluded.internet_access
        """, rows)
        
        conn.commit()
        conn.close()

    @staticmethod
    def save_prediction(prediction_dict: Dict[str, Any]) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions (
                student_id, student_name, model_used, predicted_class,
                confidence, risk_category, risk_score, probabilities_json,
                contributions_json, input_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction_dict["student_id"],
            prediction_dict.get("student_name", "Student"),
            prediction_dict["model_used"],
            prediction_dict["predicted_class"],
            float(prediction_dict["confidence"]),
            prediction_dict["risk_category"],
            float(prediction_dict["risk_score"]),
            json.dumps(prediction_dict.get("probabilities", {})),
            json.dumps(prediction_dict.get("contributing_factors", [])),
            json.dumps(prediction_dict.get("input_data", {}))
        ))
        
        conn.commit()
        pred_id = cursor.lastrowid
        conn.close()
        return pred_id

    @staticmethod
    def save_recommendation(rec_dict: Dict[str, Any]) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO recommendations (
                student_id, prediction_id, explanation, possible_causes_json,
                attention_areas_json, recommendations_json, early_interventions_json,
                llm_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec_dict["student_id"],
            rec_dict.get("prediction_id"),
            rec_dict["explanation"],
            json.dumps(rec_dict.get("possible_causes", [])),
            json.dumps(rec_dict.get("attention_areas", [])),
            json.dumps(rec_dict.get("personalized_recommendations", [])),
            json.dumps(rec_dict.get("early_interventions", [])),
            rec_dict.get("model_used", "AI-Explanation-Engine")
        ))
        
        conn.commit()
        rec_id = cursor.lastrowid
        conn.close()
        return rec_id

    @staticmethod
    def save_model_metrics(metrics_dict: Dict[str, Any]):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Ensure migration applied
        try:
            cursor.execute("ALTER TABLE model_metrics ADD COLUMN train_accuracy REAL DEFAULT 0.0;")
            conn.commit()
        except Exception:
            pass

        for model_name, m in metrics_dict.items():
            if model_name.startswith("_") or "ensemble" in model_name.lower():
                continue
            cursor.execute("""
                INSERT INTO model_metrics (
                    model_name, accuracy, train_accuracy, precision, recall, f1_score, roc_auc,
                    confusion_matrix_json, feature_importance_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model_name,
                float(m.get("accuracy", 0.0)),
                float(m.get("train_accuracy", 0.0)),
                float(m.get("precision", 0.0)),
                float(m.get("recall", 0.0)),
                float(m.get("f1_score", 0.0)),
                float(m.get("roc_auc", 0.0)) if m.get("roc_auc") is not None else None,
                json.dumps(m.get("confusion_matrix", [])),
                json.dumps(m.get("feature_importance", {}))
            ))
            
        conn.commit()
        conn.close()

    @staticmethod
    def get_latest_metrics() -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.* FROM model_metrics m
            INNER JOIN (
                SELECT model_name, MAX(trained_at) as max_date
                FROM model_metrics
                WHERE model_name NOT LIKE '%Ensemble%'
                GROUP BY model_name
            ) latest ON m.model_name = latest.model_name AND m.trained_at = latest.max_date
        """)
        
        rows = cursor.fetchall()
        result = {}
        for r in rows:
            r_dict = dict(r)
            result[r_dict["model_name"]] = {
                "accuracy": r_dict["accuracy"],
                "train_accuracy": r_dict.get("train_accuracy", r_dict["accuracy"]),
                "precision": r_dict["precision"],
                "recall": r_dict["recall"],
                "f1_score": r_dict["f1_score"],
                "roc_auc": r_dict["roc_auc"],
                "confusion_matrix": json.loads(r_dict["confusion_matrix_json"]) if r_dict.get("confusion_matrix_json") else [],
                "feature_importance": json.loads(r_dict["feature_importance_json"]) if r_dict.get("feature_importance_json") else {},
                "trained_at": r_dict["trained_at"]
            }
        conn.close()
        return result

    @staticmethod
    def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student_row = cursor.fetchone()
        
        if not student_row:
            conn.close()
            return None
            
        student = dict(student_row)
        
        # Get latest prediction
        cursor.execute("""
            SELECT * FROM predictions 
            WHERE student_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (student_id,))
        pred_row = cursor.fetchone()
        prediction = None
        if pred_row:
            prediction = dict(pred_row)
            prediction["probabilities"] = json.loads(pred_row["probabilities_json"]) if pred_row["probabilities_json"] else {}
            prediction["contributing_factors"] = json.loads(pred_row["contributions_json"]) if pred_row["contributions_json"] else []
            prediction["input_data"] = json.loads(pred_row["input_data_json"]) if pred_row["input_data_json"] else {}
            
        # Get latest recommendation
        cursor.execute("""
            SELECT * FROM recommendations 
            WHERE student_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (student_id,))
        rec_row = cursor.fetchone()
        recommendation = None
        if rec_row:
            recommendation = dict(rec_row)
            recommendation["possible_causes"] = json.loads(rec_row["possible_causes_json"]) if rec_row["possible_causes_json"] else []
            recommendation["attention_areas"] = json.loads(rec_row["attention_areas_json"]) if rec_row["attention_areas_json"] else []
            recommendation["personalized_recommendations"] = json.loads(rec_row["recommendations_json"]) if rec_row["recommendations_json"] else []
            recommendation["early_interventions"] = json.loads(rec_row["early_interventions_json"]) if rec_row["early_interventions_json"] else []
            
        conn.close()
        return {
            "student": student,
            "latest_prediction": prediction,
            "latest_recommendation": recommendation
        }

    @staticmethod
    def get_all_students(limit: int = 100, search: str = "") -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        
        if search:
            query = """
                SELECT s.*, 
                       p.predicted_class, p.risk_category, p.risk_score, p.confidence, p.model_used, p.created_at as predicted_at
                FROM students s
                LEFT JOIN predictions p ON p.id = (
                    SELECT id FROM predictions WHERE student_id = s.student_id ORDER BY created_at DESC LIMIT 1
                )
                WHERE s.student_id LIKE ? OR s.name LIKE ?
                ORDER BY s.id DESC LIMIT ?
            """
            search_param = f"%{search}%"
            cursor.execute(query, (search_param, search_param, limit))
        else:
            query = """
                SELECT s.*, 
                       p.predicted_class, p.risk_category, p.risk_score, p.confidence, p.model_used, p.created_at as predicted_at
                FROM students s
                LEFT JOIN predictions p ON p.id = (
                    SELECT id FROM predictions WHERE student_id = s.student_id ORDER BY created_at DESC LIMIT 1
                )
                ORDER BY s.id DESC LIMIT ?
            """
            cursor.execute(query, (limit,))
            
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_dashboard_statistics() -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Student count
        cursor.execute("SELECT COUNT(*) as count, AVG(attendance_percentage) as avg_att FROM students")
        row = cursor.fetchone()
        student_count = row["count"] if row else 0
        avg_att = row["avg_att"] if (row and row["avg_att"] is not None) else 0.0
        
        # Total predictions
        cursor.execute("SELECT COUNT(*) as count, AVG(risk_score) as avg_risk FROM predictions")
        p_row = cursor.fetchone()
        pred_count = p_row["count"] if p_row else 0
        avg_risk = p_row["avg_risk"] if (p_row and p_row["avg_risk"] is not None) else 0.0
        
        # Risk counts from latest prediction per student
        cursor.execute("""
            SELECT p.risk_category, COUNT(*) as cnt
            FROM predictions p
            INNER JOIN (
                SELECT student_id, MAX(created_at) as max_c
                FROM predictions
                GROUP BY student_id
            ) latest ON p.student_id = latest.student_id AND p.created_at = latest.max_c
            GROUP BY p.risk_category
        """)
        risk_map = {"Low Risk": 0, "Moderate Risk": 0, "High Risk": 0}
        for r in cursor.fetchall():
            if r["risk_category"] in risk_map:
                risk_map[r["risk_category"]] = r["cnt"]
                
        # Recent predictions
        cursor.execute("""
            SELECT id, student_id, student_name, model_used, predicted_class, confidence, risk_category, risk_score, created_at
            FROM predictions
            ORDER BY created_at DESC LIMIT 6
        """)
        recent = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {
            "total_students_in_db": student_count,
            "total_predictions": pred_count,
            "high_risk_count": risk_map["High Risk"],
            "moderate_risk_count": risk_map["Moderate Risk"],
            "low_risk_count": risk_map["Low Risk"],
            "avg_attendance": round(float(avg_att), 1),
            "avg_predicted_risk": round(float(avg_risk), 1),
            "risk_distribution": risk_map,
            "recent_predictions": recent
        }

    @staticmethod
    def save_resume_analysis(
        student_id: Optional[str],
        student_name: str,
        filename: str,
        extracted_info: Dict[str, Any],
        matched_skills: List[str],
        partial_skills: List[str],
        missing_skills: List[str],
        readiness_score: float,
        readiness_level: str,
        company_matches: List[Dict[str, Any]],
        llm_analysis: Dict[str, Any]
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resume_analyses (
                student_id, student_name, filename, extracted_info_json,
                matched_skills_json, partial_skills_json, missing_skills_json,
                readiness_score, readiness_level, company_matches_json,
                llm_analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            student_name,
            filename,
            json.dumps(extracted_info),
            json.dumps(matched_skills),
            json.dumps(partial_skills),
            json.dumps(missing_skills),
            readiness_score,
            readiness_level,
            json.dumps(company_matches),
            json.dumps(llm_analysis)
        ))
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id

    @staticmethod
    def get_recent_resume_analyses(limit: int = 10) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, student_id, student_name, filename, readiness_score,
                   readiness_level, created_at
            FROM resume_analyses
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_resume_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resume_analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        for k in ["extracted_info_json", "matched_skills_json", "partial_skills_json", "missing_skills_json", "company_matches_json", "llm_analysis_json"]:
            if res.get(k):
                try:
                    res[k.replace("_json", "")] = json.loads(res[k])
                except Exception:
                    pass
        return res
