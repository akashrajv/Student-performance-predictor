import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Briefcase,
  GraduationCap,
  Sparkles,
  TrendingUp,
  Download,
  Building2,
  Layers,
  ArrowRight,
  ShieldCheck,
  Award,
} from 'lucide-react';
import { apiService } from '../services/api';

export default function ResumeAnalyzer() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [studentsList, setStudentsList] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [alignmentFilter, setAlignmentFilter] = useState('ALL');

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      const data = await apiService.getStudents(50);
      setStudentsList(data.students || []);
    } catch (err) {
      console.warn('Could not load student list for connection:', err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setErrorMsg(null);
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedFile) {
      setErrorMsg('Please select a PDF or DOCX resume file first.');
      return;
    }

    setIsAnalyzing(true);
    setErrorMsg(null);

    try {
      const res = await apiService.analyzeResume(selectedFile, selectedStudentId || null);
      if (res.status === 'error') {
        setErrorMsg(res.message || 'Analysis failed.');
      } else {
        setAnalysisResult(res);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Failed to process resume analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Demo Presets: Create a mock File object
  const loadPreset = (presetName, sampleText, fileName) => {
    const blob = new Blob([sampleText], { type: 'text/plain' });
    const file = new File([blob], fileName, { type: fileName.endsWith('.docx') ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : 'application/pdf' });
    setSelectedFile(file);
    setErrorMsg(null);
  };

  const SAMPLE_SE_RESUME = `Akashraj Sundaram\nEmail: akashraj@example.com | Phone: +91 9876543210\nBachelor of Technology (B.Tech) in Computer Science and Engineering\nCGPA: 8.85 / 10\n\nTECHNICAL SKILLS:\nPython, Java, C++, JavaScript, TypeScript, SQL, React, Node.js, FastAPI, Spring Boot, Scikit-learn, PostgreSQL, MySQL, MongoDB, Redis, AWS, Docker, Git, Data Structures, Algorithms, OOP, System Design\n\nPROJECTS:\n1. Microservices E-Commerce: Spring Boot, Docker, PostgreSQL, AWS, Kafka. Reduced latency by 45%.\n2. Student Performance Predictor: Python, XGBoost, SHAP, React, FastAPI.\n\nEXPERIENCE:\nSoftware Engineering Intern at TechCorp Solutions.\n\nCERTIFICATIONS:\nAWS Certified Cloud Practitioner, Oracle Certified Java Programmer`;

  const SAMPLE_JUNIOR_RESUME = `Rohan Sharma\nEmail: rohan.sharma@example.com | Phone: +91 9123456780\nBachelor of Engineering (B.E.) in Information Technology\nCGPA: 6.40 / 10\n\nTECHNICAL SKILLS:\nC, HTML, CSS, Basic Python, MS Office\n\nPROJECTS:\n1. Portfolio Website: HTML5, CSS3, GitHub Pages.\n\nEXPERIENCE:\nWeb Volunteer for College Tech Fest.`;

  const SAMPLE_ANALYST_RESUME = `Kavya Patel\nEmail: kavya.patel@example.com | Phone: +91 9845123456\nBachelor of Technology in Artificial Intelligence and Data Science\nCGPA: 7.82 / 10\n\nTECHNICAL SKILLS:\nPython, SQL, R, Pandas, NumPy, Scikit-learn, Statistics, Machine Learning, Power BI, Tableau, Excel, Matplotlib, Data Structures, DBMS\n\nPROJECTS:\n1. Customer Churn Prediction: Python, Pandas, Random Forest, Power BI.\n2. Retail Sales ETL Dashboard: SQL, Python, Excel.\n\nEXPERIENCE:\nData Analytics Intern at RetailInsights.\n\nCERTIFICATIONS:\nIBM Data Science Professional Certificate`;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-blue-950 via-indigo-900 to-blue-900 rounded-2xl p-6 text-white shadow-xl border border-indigo-800">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center border border-indigo-400/30">
            <FileText className="w-5 h-5 text-indigo-300" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">AI Resume Analyzer & Placement Readiness</h1>
        </div>
        <p className="text-indigo-200 text-sm max-w-3xl leading-relaxed">
          Upload a candidate resume (PDF or DOCX) to extract technical competencies, run deterministic matching
          against active campus recruitment datasets, compute empirical placement readiness indicators, and receive
          grounded career intervention roadmaps.
        </p>
      </div>

      {/* Student Linker & Presets */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Profile linker */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
            Link Enrolled Student (Optional)
          </label>
          <select
            value={selectedStudentId}
            onChange={(e) => setSelectedStudentId(e.target.value)}
            className="w-full text-xs p-2.5 rounded-lg border border-slate-300 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">-- Standalone Candidate --</option>
            {studentsList.map((s) => (
              <option key={s.student_id} value={s.student_id}>
                {s.student_id} - {s.name} ({s.attendance_percentage}% Att, {s.previous_grade} Grade)
              </option>
            ))}
          </select>
        </div>

        {/* Demo Presets */}
        <div className="md:col-span-2 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
            Or Test Ready-to-Use Student Resume Presets
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => loadPreset('Software Engineer', SAMPLE_SE_RESUME, 'Akashraj_SE_Resume.pdf')}
              className="text-xs py-2 px-3 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded-lg border border-indigo-200 transition-colors text-center"
            >
              🌟 Software Engineer (High Match)
            </button>
            <button
              onClick={() => loadPreset('Junior Student', SAMPLE_JUNIOR_RESUME, 'Rohan_Junior_Resume.docx')}
              className="text-xs py-2 px-3 bg-amber-50 hover:bg-amber-100 text-amber-700 font-semibold rounded-lg border border-amber-200 transition-colors text-center"
            >
              🚨 Junior Student (Gaps)
            </button>
            <button
              onClick={() => loadPreset('Data Analyst', SAMPLE_DATA_ANALYST_RESUME, 'Kavya_Analyst_Resume.pdf')}
              className="text-xs py-2 px-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold rounded-lg border border-emerald-200 transition-colors text-center"
            >
              📊 Data Analyst (Domain)
            </button>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex flex-col items-center justify-center border-2 border-dashed border-indigo-200 hover:border-indigo-400 bg-indigo-50/30 rounded-xl p-6 transition-colors text-center">
          <Upload className="w-10 h-10 text-indigo-500 mb-2" />
          <h3 className="font-semibold text-slate-800 text-sm">Upload Student Resume</h3>
          <p className="text-xs text-slate-500 mb-4">Supported formats: PDF (.pdf) and Word (.docx). Max size: 10MB.</p>
          <input
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={handleFileChange}
            id="resume-file-input"
            className="hidden"
          />
          <label
            htmlFor="resume-file-input"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg cursor-pointer transition-colors shadow-sm"
          >
            Choose File
          </label>
          {selectedFile && (
            <div className="mt-3 text-xs font-medium text-emerald-600 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" /> Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
        </div>

        {errorMsg && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2">
            <XCircle className="w-4 h-4 shrink-0" /> {errorMsg}
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <button
            onClick={handleRunAnalysis}
            disabled={!selectedFile || isAnalyzing}
            className="px-6 py-2.5 bg-indigo-700 hover:bg-indigo-800 disabled:bg-slate-300 text-white font-semibold text-sm rounded-xl transition-all shadow-md flex items-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing Resume & Placement Alignment...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" /> Run AI Resume Analysis
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results View */}
      {analysisResult && (
        <div className="space-y-6">
          {/* Section 1: Candidate Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm border-t-4 border-t-indigo-600">
              <span className="text-xs font-semibold text-slate-500 uppercase">Candidate Name</span>
              <p className="text-lg font-bold text-slate-800 mt-1">{analysisResult.candidate_name}</p>
              <span className="text-xs text-slate-500">{analysisResult.filename}</span>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm border-t-4 border-t-blue-600">
              <span className="text-xs font-semibold text-slate-500 uppercase">Academic Degree</span>
              <p className="text-sm font-bold text-slate-800 mt-1">{analysisResult.education?.degree || 'Specified'}</p>
              <span className="text-xs text-slate-500">{analysisResult.education?.branch || 'General'}</span>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm border-t-4 border-t-emerald-600">
              <span className="text-xs font-semibold text-slate-500 uppercase">Graduation CGPA</span>
              <p className="text-lg font-bold text-emerald-700 mt-1">{analysisResult.education?.cgpa || 'N/A'}</p>
              <span className="text-xs text-slate-500">Eligibility baseline</span>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm border-t-4 border-t-violet-600">
              <span className="text-xs font-semibold text-slate-500 uppercase">Total Skills Extracted</span>
              <p className="text-lg font-bold text-violet-700 mt-1">{analysisResult.skills_inventory?.total_skills_count || 0}</p>
              <span className="text-xs text-slate-500">Across verified taxonomy</span>
            </div>
          </div>

          {/* Section 2: Skill Matching (Matched, Partial, Missing) */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 mb-1">Deterministic Skill Matching Engine</h2>
            <p className="text-xs text-slate-500 mb-4">
              Programmatic comparison against campus recruitment requirement benchmarks (Source of Truth).
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Matched */}
              <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <h3 className="font-semibold text-emerald-900 text-sm">
                    🟢 Matched Skills ({analysisResult.skill_analysis?.total_matched || 0})
                  </h3>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {analysisResult.skill_analysis?.matched_skills?.map((s, idx) => (
                    <span key={idx} className="px-2 py-1 bg-emerald-100 text-emerald-800 text-xs rounded-md font-medium">
                      ✓ {s}
                    </span>
                  ))}
                  {(!analysisResult.skill_analysis?.matched_skills || analysisResult.skill_analysis?.matched_skills.length === 0) && (
                    <span className="text-xs text-slate-500">No matching skills detected.</span>
                  )}
                </div>
              </div>

              {/* Partial */}
              <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-200">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                  <h3 className="font-semibold text-amber-900 text-sm">
                    🟡 Partial Skills ({analysisResult.skill_analysis?.total_partial || 0})
                  </h3>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {analysisResult.skill_analysis?.partial_skills?.map((s, idx) => (
                    <span key={idx} className="px-2 py-1 bg-amber-100 text-amber-800 text-xs rounded-md font-medium">
                      ⚠ {s}
                    </span>
                  ))}
                  {(!analysisResult.skill_analysis?.partial_skills || analysisResult.skill_analysis?.partial_skills.length === 0) && (
                    <span className="text-xs text-slate-500">No partial skills.</span>
                  )}
                </div>
              </div>

              {/* Missing */}
              <div className="p-4 rounded-xl bg-red-50/50 border border-red-200">
                <div className="flex items-center gap-2 mb-2">
                  <XCircle className="w-5 h-5 text-red-600" />
                  <h3 className="font-semibold text-red-900 text-sm">
                    🔴 Missing Skills ({analysisResult.skill_analysis?.total_missing || 0})
                  </h3>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-2 max-h-48 overflow-y-auto">
                  {analysisResult.skill_analysis?.missing_skills?.slice(0, 15).map((s, idx) => (
                    <span key={idx} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-md font-medium">
                      ✗ {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Empirical Skill Priority */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 mb-1">Empirical Skill Demand Priority</h2>
            <p className="text-xs text-slate-500 mb-4">
              Prioritizes missing competencies using exact recruitment frequencies calculated across the campus company dataset.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-orange-50/60 border border-orange-200">
                <h4 className="font-bold text-orange-900 text-sm mb-2">🔥 High Priority (≥ 30% companies)</h4>
                <div className="space-y-1.5">
                  {analysisResult.skill_priority?.['High Priority']?.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs p-1.5 bg-white rounded border border-orange-100">
                      <span className="font-semibold text-slate-800">{item.skill}</span>
                      <span className="text-orange-700 font-bold">{item.frequency_count} companies ({item.frequency_percentage}%)</span>
                    </div>
                  ))}
                  {(!analysisResult.skill_priority?.['High Priority'] || analysisResult.skill_priority?.['High Priority'].length === 0) && (
                    <p className="text-xs text-slate-500">No high-priority missing skills.</p>
                  )}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200">
                <h4 className="font-bold text-amber-900 text-sm mb-2">⚠ Medium Priority (15% - 29% companies)</h4>
                <div className="space-y-1.5">
                  {analysisResult.skill_priority?.['Medium Priority']?.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs p-1.5 bg-white rounded border border-amber-100">
                      <span className="font-semibold text-slate-800">{item.skill}</span>
                      <span className="text-amber-700 font-bold">{item.frequency_count} companies ({item.frequency_percentage}%)</span>
                    </div>
                  ))}
                  {(!analysisResult.skill_priority?.['Medium Priority'] || analysisResult.skill_priority?.['Medium Priority'].length === 0) && (
                    <p className="text-xs text-slate-500">No medium-priority missing skills.</p>
                  )}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <h4 className="font-bold text-slate-800 text-sm mb-2">ℹ Low Priority (&lt; 15% companies)</h4>
                <div className="space-y-1.5 max-h-48 overflow-y-auto">
                  {analysisResult.skill_priority?.['Low Priority']?.slice(0, 6).map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs p-1.5 bg-white rounded border border-slate-200">
                      <span className="font-semibold text-slate-800">{item.skill}</span>
                      <span className="text-slate-600 font-bold">{item.frequency_count} companies ({item.frequency_percentage}%)</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Section 4: Placement Readiness Score */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 mb-1">🎯 Placement Readiness Score</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center mt-4">
              <div className="flex flex-col items-center justify-center p-6 bg-slate-50 rounded-2xl border border-slate-200">
                <div className="text-4xl font-black text-indigo-900 mb-1">
                  {analysisResult.placement_readiness?.readiness_score || 0}%
                </div>
                <span className="text-xs uppercase font-bold tracking-wider text-slate-500 text-center">
                  Project-defined Placement Readiness Score
                </span>
                <span className="mt-3 px-3 py-1 bg-indigo-100 text-indigo-800 font-bold text-xs rounded-full text-center">
                  {analysisResult.placement_readiness?.readiness_level}
                </span>
              </div>

              <div className="md:col-span-2 space-y-3">
                <p className="text-sm text-slate-700 font-medium">
                  {analysisResult.placement_readiness?.summary_description}
                </p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="text-slate-500">Core Requirement Coverage:</span>
                    <span className="font-bold text-slate-800 ml-1">{analysisResult.placement_readiness?.score_breakdown?.core_requirements_score || 0} / 45 pts</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="text-slate-500">Market Demand Adoption:</span>
                    <span className="font-bold text-slate-800 ml-1">{analysisResult.placement_readiness?.score_breakdown?.market_priority_score || 0} / 20 pts</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="text-slate-500">Practical Portfolio:</span>
                    <span className="font-bold text-slate-800 ml-1">{analysisResult.placement_readiness?.score_breakdown?.practical_projects_score || 0} / 15 pts</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="text-slate-500">Industry Exposure & Credentials:</span>
                    <span className="font-bold text-slate-800 ml-1">{((analysisResult.placement_readiness?.score_breakdown?.internship_experience_score || 0) + (analysisResult.placement_readiness?.score_breakdown?.certifications_academic_score || 0)).toFixed(1)} / 20 pts</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 italic">
                  ℹ️ {analysisResult.placement_readiness?.disclaimer}
                </p>
              </div>
            </div>
          </div>

          {/* Section 5: Company & Role Alignment */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-lg font-bold text-slate-800">Company & Role Alignment</h2>
                <p className="text-xs text-slate-500">Evaluated against verified companies in the recruitment dataset.</p>
              </div>
              <div className="flex gap-2">
                {['ALL', 'High Alignment', 'Moderate Alignment', 'Low Alignment'].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setAlignmentFilter(lvl)}
                    className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                      alignmentFilter === lvl
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-100 text-slate-700 border-b border-slate-200">
                    <th className="p-3 font-semibold">Company</th>
                    <th className="p-3 font-semibold">Job Role</th>
                    <th className="p-3 font-semibold">Alignment</th>
                    <th className="p-3 font-semibold">Coverage</th>
                    <th className="p-3 font-semibold">Matched Skills</th>
                    <th className="p-3 font-semibold">Missing Skills</th>
                    <th className="p-3 font-semibold">Academic Eligibility</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {analysisResult.company_matching
                    ?.filter((c) => alignmentFilter === 'ALL' || c.alignment === alignmentFilter)
                    ?.map((comp, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/80">
                        <td className="p-3 font-bold text-slate-900">{comp.company}</td>
                        <td className="p-3 text-slate-700">{comp.role}</td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                              comp.alignment === 'High Alignment'
                                ? 'bg-emerald-100 text-emerald-800'
                                : comp.alignment === 'Moderate Alignment'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-700'
                            }`}
                          >
                            {comp.alignment}
                          </span>
                        </td>
                        <td className="p-3 font-semibold text-slate-800">{comp.match_score}%</td>
                        <td className="p-3 text-emerald-700">{comp.matched_skills?.slice(0, 3).join(', ') || 'None'}</td>
                        <td className="p-3 text-red-700">{comp.missing_skills?.slice(0, 3).join(', ') || 'None'}</td>
                        <td className="p-3 text-slate-600">{comp.cgpa_note}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 6: AI LLM Strategic Insights */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm border-l-8 border-l-indigo-700">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-5 h-5 text-indigo-600" />
              <h2 className="text-lg font-bold text-slate-800">AI Gap Analysis & LLM Strategic Insights</h2>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Generated by {analysisResult.llm_analysis?.model_used} grounded directly in candidate findings.
            </p>

            <div className="p-4 bg-indigo-50/60 rounded-xl mb-4 text-xs text-indigo-950 leading-relaxed">
              <span className="font-bold block mb-1">Executive Summary:</span>
              {analysisResult.llm_analysis?.resume_summary}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                <h4 className="font-bold text-slate-800 text-xs uppercase mb-2">Key Strengths</h4>
                <ul className="space-y-1.5 text-xs text-slate-700 list-disc list-inside">
                  {analysisResult.llm_analysis?.main_strengths?.map((s, idx) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                <h4 className="font-bold text-slate-800 text-xs uppercase mb-2">Primary Identified Skill Gaps</h4>
                <ul className="space-y-1.5 text-xs text-slate-700 list-disc list-inside">
                  {analysisResult.llm_analysis?.important_skill_gaps?.map((g, idx) => (
                    <li key={idx}>{g}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Section 7: Personalized Improvement Plan */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 mb-1">🚀 Personalized Placement Improvement Plan</h2>
            <p className="text-xs text-slate-500 mb-4">
              Actionable sequence of concrete learning and project interventions.
            </p>
            <div className="space-y-3">
              {analysisResult.personalized_improvement_plan?.map((card, idx) => (
                <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 transition-all shadow-sm">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs font-bold text-indigo-700 uppercase tracking-wide">
                      {card.priority_level}: {card.title}
                    </span>
                    <span className="text-[11px] font-semibold px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
                      {card.timeline}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mb-1">
                    <b>Target Gap:</b> {card.missing_skill} ({card.gap_type})
                  </p>
                  <p className="text-xs text-slate-800 mb-2 font-medium">
                    <b>Recommended Action:</b> {card.action}
                  </p>
                  <div className="p-2.5 bg-emerald-50/70 border border-emerald-200 rounded-lg text-xs text-emerald-900">
                    <b>💡 Practical Implementation:</b> {card.project_recommendation}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(analysisResult, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `resume_analysis_${analysisResult.candidate_name.replace(/\s+/g, '_')}.json`;
                  a.click();
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg flex items-center gap-2 shadow-sm"
              >
                <Download className="w-4 h-4" /> Export Complete Analysis Report (JSON)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
