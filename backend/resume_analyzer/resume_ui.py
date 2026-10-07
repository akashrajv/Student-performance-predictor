import asyncio
import io
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.config import settings
from backend.services.db_service import DatabaseService
from backend.resume_analyzer.service import ResumeAnalyzerService
from backend.resume_analyzer.recruitment_analyzer import RecruitmentAnalyzer
from backend.resume_analyzer.skill_matcher import SkillMatcher
from backend.resume_analyzer.placement_readiness import PlacementReadinessEngine

# Preset sample resume texts for rapid demonstration & verification
SAMPLE_HIGH_MATCH_RESUME = """
Akashraj Sundaram
Email: akashraj.dev@example.com | Phone: +91 9876543210
LinkedIn: linkedin.com/in/akashraj-dev | GitHub: github.com/akashraj-dev
Bachelor of Technology (B.Tech) in Computer Science and Engineering
ABC Institute of Technology | CGPA: 8.85 / 10

TECHNICAL SKILLS:
- Programming Languages: Python, Java, C++, JavaScript, TypeScript, SQL
- Frameworks & Libraries: React, Node.js, FastAPI, Spring Boot, Scikit-learn, Pandas, NumPy
- Databases & Cloud: PostgreSQL, MySQL, MongoDB, Redis, AWS (EC2, S3), Docker, Git
- Core Computer Science: Data Structures, Algorithms, Object-Oriented Programming (OOP), System Design, Computer Networks, Operating Systems

PROJECTS:
1. Cloud-Based Microservices E-Commerce Platform
- Developed scalable microservices backend with Spring Boot, Docker, and PostgreSQL.
- Implemented asynchronous event streaming using Apache Kafka and Redis caching, reducing API latency by 45%.
- Deployed services to AWS using Docker containers and automated CI/CD pipelines.

2. Student Academic Performance Predictor & Early Warning System
- Built multi-model predictive engine using Python, Scikit-learn, and XGBoost with 95.8% accuracy.
- Integrated Explainable AI (SHAP attributions) and automated LLM-grounded intervention reporting.
- Designed interactive web portal in React with real-time risk classification.

EXPERIENCE:
- Software Engineering Intern at TechCorp Solutions (Jan 2024 - June 2024)
  Collaborated on REST API optimizations, migrated relational database schemas, and authored unit tests improving test coverage to 88%.

CERTIFICATIONS:
- AWS Certified Cloud Practitioner
- Oracle Certified Associate Java Programmer
- HackerRank Problem Solving (Advanced)
"""

SAMPLE_GAP_HEAVY_RESUME = """
Rohan Sharma
Email: rohan.sharma@example.com | Phone: +91 9123456780
Bachelor of Engineering (B.E.) in Information Technology
City College of Engineering | CGPA: 6.40 / 10

TECHNICAL SKILLS:
- Languages: C, HTML, CSS, Basic Python
- Tools: VS Code, MS Word, Excel

PROJECTS:
1. Personal Portfolio Website
- Created responsive personal webpage using HTML5 and CSS3.
- Hosted on GitHub Pages.

EXPERIENCE:
- Volunteer Web Coordinator for College Tech Fest.

CERTIFICATIONS:
- Certificate of Participation in Web Design Workshop.
"""

SAMPLE_DATA_ANALYST_RESUME = """
Kavya Patel
Email: kavya.patel@example.com | Phone: +91 9845123456
GitHub: github.com/kavya-analytics | LinkedIn: linkedin.com/in/kavya-data
Bachelor of Technology (B.Tech) in Artificial Intelligence and Data Science
National Institute of Science | CGPA: 7.82 / 10

TECHNICAL SKILLS:
- Programming & Query Languages: Python, SQL, R
- Data Science & ML: Pandas, NumPy, Scikit-learn, Statistics, Machine Learning, Data Visualization
- Business Intelligence & Tools: Power BI, Tableau, Excel, Matplotlib, Seaborn, Git
- Core Concepts: Data Structures, DBMS, Exploratory Data Analysis, Data Warehousing

PROJECTS:
1. Customer Churn Analytics & Predictive Modeling
- Analyzed telecom customer behavior dataset with 10,000+ records using Python and Pandas.
- Built Random Forest classification model achieving 82% F1-score to identify churn risk factors.
- Designed interactive Power BI dashboard for executive KPI tracking.

2. Retail Sales Performance Dashboard
- Formulated complex SQL queries (multi-table joins, window functions) to extract revenue trends.
- Automated weekly ETL reporting using Python scripts.

EXPERIENCE:
- Data Analytics Intern at RetailInsights (Summer 2024)
  Extracted and cleaned sales transaction data using SQL and Python; formulated automated dashboards.

CERTIFICATIONS:
- IBM Data Science Professional Certificate
"""

def render_resume_analyzer_page():
    """Render the AI Resume Analyzer & Placement Readiness Streamlit Dashboard."""
    st.markdown("""
    <div class='hero-banner'>
        <h1 style='color: white; margin: 0; font-size: 1.8rem;'>📄 AI Resume Analyzer & Placement Readiness</h1>
        <p style='color: #94a3b8; margin-top: 6px; font-size: 0.95rem;'>
            Extracts resume information, performs deterministic skill matching against campus recruitment datasets,
            calculates placement readiness indicators, and delivers grounded LLM career interventions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Inspect recruitment dataset status
    rec_analyzer = RecruitmentAnalyzer()
    status = rec_analyzer.get_status()

    # Top Alert / Status Ribbon
    if status["available"]:
        st.caption(f"✓ Recruitment Dataset Active: **{status['record_count']} Company Requirements** loaded from `{status['detected_columns'].get('company', 'Company')}` & `{status['detected_columns'].get('required_skills', 'Required_Skills')}`")
    else:
        st.warning(f"⚠️ {status.get('error', 'Recruitment dataset not loaded.')}")

    # Student Profile Integration (Section 16)
    with st.expander("👤 Connect with Enrolled Student Profile (Optional)", expanded=False):
        all_students = DatabaseService.get_all_students()
        student_opts = ["-- Analyze as Standalone Candidate --"] + [f"{s['student_id']} - {s['name']} (Att: {s['attendance_percentage']}%, Grade: {s['previous_grade']})" for s in all_students]
        selected_student_str = st.selectbox("Select Enrolled Student Record:", student_opts)
        
        selected_student_id = None
        if selected_student_str != student_opts[0]:
            selected_student_id = selected_student_str.split(" - ")[0].strip()
            student_rec = DatabaseService.get_student_by_id(selected_student_id)
            preds = DatabaseService.get_predictions_by_student(selected_student_id)
            if student_rec:
                scol1, scol2, scol3, scol4 = st.columns(4)
                with scol1:
                    st.metric("Enrolled Student", student_rec["name"])
                with scol2:
                    st.metric("Attendance", f"{student_rec['attendance_percentage']}%")
                with scol3:
                    st.metric("Academic Standing", f"{student_rec['previous_grade']}/100")
                with scol4:
                    if preds:
                        latest = preds[0]
                        st.metric("Academic Prediction", f"{latest['predicted_class']} ({latest['risk_category']})")
                    else:
                        st.metric("Academic Prediction", "No prior inference")

    st.markdown("---")

    # Upload & Preset Section
    col_upload, col_presets = st.columns([1.2, 1])

    with col_upload:
        st.subheader("1. Upload Resume Document")
        st.caption("Supported formats: **PDF (.pdf)** and **Word (.docx)**. Max size: 10MB.")
        uploaded_file = st.file_uploader(
            "Choose resume file",
            type=["pdf", "docx"],
            help="Upload student's PDF or DOCX resume document for automated parsing and skill extraction."
        )

    with col_presets:
        st.subheader("2. Or Test Sample Resume Presets")
        st.caption("Click to load pre-configured student resumes with different skill profiles:")
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            if st.button("🌟 Software Engineer\n(High Match)", use_container_width=True):
                st.session_state["demo_resume_text"] = SAMPLE_HIGH_MATCH_RESUME
                st.session_state["demo_resume_name"] = "Akashraj_Sundaram_Resume.pdf"
        with p_col2:
            if st.button("🚨 Junior Student\n(High Gaps)", use_container_width=True):
                st.session_state["demo_resume_text"] = SAMPLE_GAP_HEAVY_RESUME
                st.session_state["demo_resume_name"] = "Rohan_Sharma_Resume.docx"
        with p_col3:
            if st.button("📊 Data Analyst\n(Domain Match)", use_container_width=True):
                st.session_state["demo_resume_text"] = SAMPLE_DATA_ANALYST_RESUME
                st.session_state["demo_resume_name"] = "Kavya_Patel_Resume.pdf"

    # Determine input source
    resume_source = None
    resume_filename = ""

    if uploaded_file is not None:
        resume_source = uploaded_file.getvalue()
        resume_filename = uploaded_file.name
    elif "demo_resume_text" in st.session_state:
        resume_source = st.session_state["demo_resume_text"]
        resume_filename = st.session_state.get("demo_resume_name", "sample_resume.pdf")

    # Analyze Button
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Run AI Resume & Placement Analysis", type="primary", use_container_width=True, disabled=(resume_source is None))

    if analyze_btn and resume_source:
        with st.spinner("Executing end-to-end resume extraction, deterministic skill matching, and LLM gap analysis..."):
            try:
                # Run async analysis
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                analysis_result = loop.run_until_complete(
                    ResumeAnalyzerService.analyze_resume(
                        file_source=resume_source,
                        filename=resume_filename,
                        student_id=selected_student_id,
                        save_to_db=True
                    )
                )
                st.session_state["last_resume_analysis"] = analysis_result
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                return

    # Display Analysis Results
    if "last_resume_analysis" in st.session_state:
        res = st.session_state["last_resume_analysis"]
        if res.get("status") == "error":
            st.error(f"❌ {res.get('message', 'An error occurred during resume analysis.')}")
            return

        st.success(f"✓ Analysis complete for **{res.get('candidate_name')}** ({res.get('filename')})")

        # ----------------------------------------------------------------------
        # Section A: Resume Summary & Overview
        # ----------------------------------------------------------------------
        st.markdown("### 📋 Candidate Profile & Resume Summary")
        cand_edu = res.get("education", {})
        cand_contact = res.get("contact", {})
        readiness = res.get("placement_readiness", {})

        kcol1, kcol2, kcol3, kcol4 = st.columns(4)
        with kcol1:
            st.metric("Candidate Name", res.get("candidate_name", "Candidate"))
        with kcol2:
            st.metric("Degree & Branch", f"{cand_edu.get('degree', 'N/A')} - {cand_edu.get('branch', 'N/A')}")
        with kcol3:
            st.metric("Academic CGPA", cand_edu.get("cgpa", "N/A"))
        with kcol4:
            st.metric("Total Skills Detected", res.get("skills_inventory", {}).get("total_skills_count", 0))

        # Quality observation card
        quality = res.get("resume_quality", {})
        with st.expander("🔍 Resume Structure & Quality Observations", expanded=False):
            st.markdown(f"**Resume Quality Index:** `{quality.get('quality_score', 0)} / 100`")
            qcol1, qcol2 = st.columns(2)
            with qcol1:
                st.markdown("**✓ Notable Positive Observations:**")
                for obs in quality.get("observations", []):
                    st.markdown(f"- {obs}")
            with qcol2:
                st.markdown("**💡 Areas for Structural Improvement:**")
                for imp in quality.get("improvements", []):
                    st.markdown(f"- {imp}")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # Section B: Skill Matching (Matched / Partial / Missing)
        # ----------------------------------------------------------------------
        st.markdown("### 🔍 Deterministic Skill Matching Engine")
        st.caption("Compared candidate resume skills against all target competencies identified in the campus recruitment dataset.")

        skills_info = res.get("skill_analysis", {})
        matched_list = skills_info.get("matched_skills", [])
        partial_list = skills_info.get("partial_skills", [])
        missing_list = skills_info.get("missing_skills", [])

        scol1, scol2, scol3 = st.columns(3)
        with scol1:
            st.markdown(f"#### 🟢 Matched Skills ({len(matched_list)})")
            st.caption("Verified in resume")
            if matched_list:
                st.write(", ".join(matched_list))
            else:
                st.info("No exact matching skills found.")

        with scol2:
            st.markdown(f"#### 🟡 Partial Skills ({len(partial_list)})")
            st.caption("Related foundations present")
            if partial_list:
                st.write(", ".join(partial_list))
            else:
                st.info("No partially matched skills.")

        with scol3:
            st.markdown(f"#### 🔴 Missing Skills ({len(missing_list)})")
            st.caption("Recruitment gaps identified")
            if missing_list:
                st.write(", ".join(missing_list[:15]))
            else:
                st.success("All target skills satisfied!")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # Section C: Skill Priority (Empirical Dataset Frequency)
        # ----------------------------------------------------------------------
        st.markdown("### 📊 Empirical Skill Priority Analysis")
        st.caption("Prioritizes missing skills using exact requirement frequencies calculated across all companies in the recruitment dataset.")

        prio_tiers = res.get("skill_priority", {})
        high_prio = prio_tiers.get("High Priority", [])
        med_prio = prio_tiers.get("Medium Priority", [])
        low_prio = prio_tiers.get("Low Priority", [])

        pcol1, pcol2, pcol3 = st.columns(3)
        with pcol1:
            st.markdown(f"#### 🔥 High Priority ({len(high_prio)})")
            st.caption("Required by ≥ 30% of companies")
            if high_prio:
                for hp in high_prio[:5]:
                    st.markdown(f"- **{hp['skill']}** ({hp['frequency_count']} companies • `{hp['frequency_percentage']}%`)")
            else:
                st.info("No high-priority missing skills.")

        with pcol2:
            st.markdown(f"#### ⚠ Medium Priority ({len(med_prio)})")
            st.caption("Required by 15% - 29% of companies")
            if med_prio:
                for mp in med_prio[:5]:
                    st.markdown(f"- **{mp['skill']}** ({mp['frequency_count']} companies • `{mp['frequency_percentage']}%`)")
            else:
                st.info("No medium-priority missing skills.")

        with pcol3:
            st.markdown(f"#### ℹ Low Priority ({len(low_prio)})")
            st.caption("Niche / specialized skills (< 15%)")
            if low_prio:
                for lp in low_prio[:5]:
                    st.markdown(f"- **{lp['skill']}** ({lp['frequency_count']} companies • `{lp['frequency_percentage']}%`)")
            else:
                st.info("No low-priority missing skills.")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # Section D: Company-Wise Alignment Matching
        # ----------------------------------------------------------------------
        st.markdown("### 🏢 Company & Job Role Alignment")
        st.caption("Role-by-role evaluation against active recruitment postings in the project database.")

        comp_matches = res.get("company_matching", [])
        if comp_matches:
            # Filter control
            align_filter = st.selectbox(
                "Filter by Alignment Level:",
                ["All Alignment Levels", "High Alignment (≥ 70%)", "Moderate Alignment (40% - 69%)", "Low Alignment (< 40%)"]
            )

            filtered_comps = comp_matches
            if "High" in align_filter:
                filtered_comps = [c for c in comp_matches if c["alignment"] == "High Alignment"]
            elif "Moderate" in align_filter:
                filtered_comps = [c for c in comp_matches if c["alignment"] == "Moderate Alignment"]
            elif "Low" in align_filter:
                filtered_comps = [c for c in comp_matches if c["alignment"] == "Low Alignment"]

            # Display table / cards
            comp_table_data = []
            for c in filtered_comps:
                comp_table_data.append({
                    "Company": c["company"],
                    "Role": c["role"],
                    "Department": c["department"],
                    "Alignment": c["alignment"],
                    "Coverage (%)": f"{c['match_score']}%",
                    "Matched Skills": ", ".join(c["matched_skills"][:4]) or "None",
                    "Missing Skills": ", ".join(c["missing_skills"][:4]) or "None",
                    "Eligibility": c["cgpa_note"]
                })

            st.dataframe(pd.DataFrame(comp_table_data), use_container_width=True, hide_index=True)
        else:
            st.info("No company recruitment records available to match.")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # Section E: Placement Readiness Score
        # ----------------------------------------------------------------------
        st.markdown("### 🎯 Placement Readiness")
        r_score = readiness.get("readiness_score", 0.0)
        r_level = readiness.get("readiness_level", "Developing")
        r_desc = readiness.get("summary_description", "")

        read_col1, read_col2 = st.columns([1, 1.5])
        with read_col1:
            # Gauge chart for score
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=r_score,
                number={"suffix": "%", "font": {"size": 36, "color": "#1e3a8a"}},
                title={"text": "Project-defined Placement Readiness Score", "font": {"size": 14, "color": "#1e3a8a"}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8"},
                    "bar": {"color": "#1e3a8a"},
                    "steps": [
                        {"range": [0, 40], "color": "#fee2e2"},
                        {"range": [40, 60], "color": "#ffedd5"},
                        {"range": [60, 80], "color": "#fef3c7"},
                        {"range": [80, 100], "color": "#dcfce7"}
                    ],
                    "threshold": {
                        "line": {"color": "#059669", "width": 4},
                        "thickness": 0.75,
                        "value": 80
                    }
                }
            ))
            fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with read_col2:
            st.markdown(f"#### **Status:** `{r_level}`")
            st.markdown(f"<p style='color: #334155;'>{r_desc}</p>", unsafe_allow_html=True)
            
            # Score breakdown
            b_down = readiness.get("score_breakdown", {})
            st.markdown("**Index Factor Breakdown:**")
            st.markdown(f"- Core Requirements Coverage: `{b_down.get('core_requirements_score', 0)} / 45 pts`")
            st.markdown(f"- Market Demand Skill Adoption: `{b_down.get('market_priority_score', 0)} / 20 pts`")
            st.markdown(f"- Practical Portfolio Projects: `{b_down.get('practical_projects_score', 0)} / 15 pts`")
            st.markdown(f"- Industry Exposure / Experience: `{b_down.get('internship_experience_score', 0)} / 10 pts`")
            st.markdown(f"- Academic Baseline & Credentials: `{b_down.get('certifications_academic_score', 0)} / 10 pts`")

            st.caption(f"ℹ️ {readiness.get('disclaimer', '')}")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # Section F: AI Gap Analysis (Existing LLM Engine)
        # ----------------------------------------------------------------------
        st.markdown("### 💬 AI Gap Analysis & LLM Strategic Insights")
        llm_data = res.get("llm_analysis", {})
        st.caption(f"Generated via **{llm_data.get('model_used', 'Grounded Pedagogical LLM')}** based strictly on resume and recruitment data.")

        st.markdown("""
        <div class='report-card'>
            <h4 style='color: #1e3a8a; margin-top: 0;'>📝 Comprehensive Executive Summary</h4>
            <p style='color: #334155;'>""" + llm_data.get("resume_summary", "") + """</p>
        </div>
        """, unsafe_allow_html=True)

        gap_c1, gap_c2 = st.columns(2)
        with gap_c1:
            st.markdown("#### 💪 Key Demonstrated Strengths")
            for s in llm_data.get("main_strengths", []):
                st.markdown(f"- {s}")

            st.markdown("#### 🚀 Project Enhancement Advice")
            for p in llm_data.get("project_improvement_suggestions", []):
                st.markdown(f"- {p}")

        with gap_c2:
            st.markdown("#### 🎯 Critical Identified Skill Gaps")
            for g in llm_data.get("important_skill_gaps", []):
                st.markdown(f"- {g}")

            st.markdown("#### 🏢 Company-Specific Preparation Advice")
            for c in llm_data.get("company_specific_preparation_advice", []):
                st.markdown(f"- {c}")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # Section G: Personalized Improvement Plan
        # ----------------------------------------------------------------------
        st.markdown("### 🚀 Personalized Placement Improvement Plan")
        st.caption("Actionable, timeline-sequenced intervention plan grounded directly in identified skill gaps.")

        plan_items = res.get("personalized_improvement_plan", [])
        for item in plan_items:
            with st.container():
                st.markdown(f"""
                <div style='background: white; border: 1px solid #cbd5e1; border-left: 5px solid #1e3a8a; border-radius: 10px; padding: 16px; margin-bottom: 14px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h4 style='color: #1e3a8a; margin: 0;'>{item.get('priority_level')}: {item.get('title')}</h4>
                        <span style='background: #e0f2fe; color: #0369a1; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;'>{item.get('timeline')}</span>
                    </div>
                    <p style='color: #475569; margin: 6px 0 8px 0; font-size: 0.85rem;'><b>Focus Gap:</b> {item.get('missing_skill')} ({item.get('gap_type')})</p>
                    <p style='color: #1e293b; margin-bottom: 8px;'><b>Recommended Action:</b> {item.get('action')}</p>
                    <p style='color: #0f766e; background: #f0fdf4; padding: 8px 12px; border-radius: 6px; margin: 0; font-size: 0.88rem;'><b>💡 Practical Implementation:</b> {item.get('project_recommendation')}</p>
                </div>
                """, unsafe_allow_html=True)

        # Download Report JSON
        st.markdown("<br>", unsafe_allow_html=True)
        report_json = json.dumps(res, indent=2, default=str)
        st.download_button(
            label="📥 Download Full Resume Analysis Report (JSON)",
            data=report_json,
            file_name=f"resume_analysis_{res.get('candidate_name', 'student').replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
