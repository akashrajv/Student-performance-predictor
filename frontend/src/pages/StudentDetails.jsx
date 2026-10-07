import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  User,
  GraduationCap,
  CalendarCheck,
  Clock,
  BookOpen,
  Award,
  Sparkles,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  Printer,
} from 'lucide-react';
import { apiService } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import FactorBreakdown from '../components/FactorBreakdown';
import LLMExplanationCard from '../components/LLMExplanationCard';

export default function StudentDetails({ initialStudentId = null, onPredictForStudent }) {
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState(initialStudentId);
  const [studentDetail, setStudentDetail] = useState(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [llmLoading, setLlmLoading] = useState(false);
  const [llmResult, setLlmResult] = useState(null);

  useEffect(() => {
    loadStudents();
  }, [search]);

  useEffect(() => {
    if (selectedStudentId) {
      loadStudentDetail(selectedStudentId);
    }
  }, [selectedStudentId]);

  const loadStudents = async () => {
    try {
      const res = await apiService.getStudents(60, search);
      setStudents(res.students || []);
      if (!selectedStudentId && res.students && res.students.length > 0) {
        setSelectedStudentId(res.students[0].student_id);
      }
    } catch (err) {
      console.error('Error fetching students:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStudentDetail = async (id) => {
    setDetailLoading(true);
    setLlmResult(null);
    try {
      const res = await apiService.getStudentById(id);
      setStudentDetail(res);
      if (res.latest_recommendation) {
        setLlmResult(res.latest_recommendation);
      }
    } catch (err) {
      console.error('Error loading student detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleGenerateLLM = async () => {
    if (!studentDetail?.latest_prediction) return;
    setLlmLoading(true);
    const pred = studentDetail.latest_prediction;
    const stu = studentDetail.student;

    try {
      const payload = {
        student_id: stu.student_id,
        student_name: stu.name,
        input_data: stu,
        predicted_class: pred.predicted_class,
        confidence: pred.confidence,
        risk_category: pred.risk_category,
        risk_score: pred.risk_score,
        contributing_factors: pred.contributing_factors,
        prediction_id: pred.id,
      };
      const res = await apiService.explainPrediction(payload);
      setLlmResult(res);
    } catch (err) {
      console.error('LLM generation error:', err);
    } finally {
      setLlmLoading(false);
    }
  };

  const student = studentDetail?.student;
  const prediction = studentDetail?.latest_prediction;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page Title */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Users className="w-5 h-5 text-indigo-400" />
          Student Academic Directory & 360° Profiles
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Search student records, review current risk levels, analyze individual feature attributions, and generate customized academic interventions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Student List & Search */}
        <div className="lg:col-span-4 space-y-3">
          <div className="p-4 rounded-2xl glass-card border border-slate-800 space-y-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search by ID or name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:border-indigo-500 outline-none"
              />
            </div>

            <div className="overflow-y-auto max-h-[580px] space-y-1.5 pr-1">
              {students.map((s) => {
                const isSelected = s.student_id === selectedStudentId;
                return (
                  <div
                    key={s.student_id}
                    onClick={() => setSelectedStudentId(s.student_id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'border-indigo-500 bg-indigo-950/40 shadow-sm'
                        : 'border-slate-800/80 bg-slate-900/40 hover:bg-slate-800/40'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-1.5">
                      <div>
                        <div className="text-xs font-bold text-white leading-tight">
                          {s.name}
                        </div>
                        <div className="text-[11px] font-mono text-slate-400">
                          {s.student_id}
                        </div>
                      </div>
                      {s.risk_category && (
                        <RiskBadge risk={s.risk_category} size="sm" />
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-2 pt-2 border-t border-slate-800/60 font-mono">
                      <span>Att: {s.attendance_percentage}%</span>
                      <span>Study: {s.study_hours_per_week}h</span>
                      <span>Grade: {s.previous_grade}</span>
                    </div>
                  </div>
                );
              })}

              {students.length === 0 && (
                <div className="text-center py-8 text-xs text-slate-500">
                  No matching student records found.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Student 360 Dossier */}
        <div className="lg:col-span-8 space-y-6">
          {detailLoading ? (
            <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-3">
              <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
              <p className="text-xs">Loading student profile...</p>
            </div>
          ) : student ? (
            <div className="space-y-6">
              {/* Profile Card Header */}
              <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-indigo-600/20">
                      {student.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">
                        {student.name}
                      </h3>
                      <div className="text-xs text-slate-400 font-mono flex items-center gap-2">
                        <span>ID: {student.student_id}</span>
                        <span>•</span>
                        <span>Parent Education: {student.parental_education}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {prediction ? (
                      <RiskBadge risk={prediction.risk_category} size="lg" />
                    ) : (
                      <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700">
                        Not Evaluated Yet
                      </span>
                    )}
                  </div>
                </div>

                {/* Academic Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase">
                      Attendance Rate
                    </span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {student.attendance_percentage}%
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase">
                      Study Hours / Wk
                    </span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {student.study_hours_per_week} hrs
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase">
                      Previous Grade
                    </span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {student.previous_grade} / 100
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase">
                      Assessment Score
                    </span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {student.assessment_score} / 100
                    </div>
                  </div>
                </div>

                {/* Secondary Indicators */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-300">
                  <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 block">Assignments:</span>
                    <strong className="font-mono">{student.assignment_score} / 100</strong>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 block">Sleep Duration:</span>
                    <strong className="font-mono">{student.sleep_hours} hrs/night</strong>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 block">Tutoring Sessions:</span>
                    <strong className="font-mono">{student.tutoring_sessions} sessions</strong>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 block">Extracurricular:</span>
                    <strong>{student.extracurricular_activities}</strong>
                  </div>
                </div>
              </div>

              {/* Latest Model Prediction & Explainability */}
              {prediction ? (
                <div className="space-y-6">
                  {/* Model Score Header */}
                  <div className="p-6 rounded-2xl glass-card border border-indigo-500/25 space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                      <div>
                        <h4 className="text-sm font-bold text-white">
                          Latest Prediction Outcome
                        </h4>
                        <span className="text-xs text-slate-400">
                          Evaluated by {prediction.model_used} on {new Date(prediction.created_at).toLocaleString()}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <span className="text-[10px] text-slate-400 uppercase block">
                            Confidence
                          </span>
                          <span className="text-xs font-mono font-bold text-indigo-400">
                            {Math.round(prediction.confidence * 100)}%
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] text-slate-400 uppercase block">
                            Risk Index
                          </span>
                          <span className="text-xs font-mono font-bold text-rose-400">
                            {prediction.risk_score}%
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Contributing Factors */}
                    <FactorBreakdown
                      factors={prediction.contributing_factors}
                      predictedClass={prediction.predicted_class}
                      riskCategory={prediction.risk_category}
                    />
                  </div>

                  {/* LLM Explanation Card */}
                  <LLMExplanationCard
                    explanationData={llmResult}
                    loading={llmLoading}
                    onGenerate={handleGenerateLLM}
                  />
                </div>
              ) : (
                <div className="p-8 rounded-2xl glass-card border border-dashed border-slate-800 text-center space-y-3">
                  <p className="text-xs text-slate-400">
                    This student does not have a prediction logged yet.
                  </p>
                  <button
                    onClick={() => {
                      if (onPredictForStudent) onPredictForStudent(student);
                    }}
                    className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all cursor-pointer inline-flex items-center gap-2"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Run Performance Prediction Now</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 text-xs glass-card rounded-2xl">
              Select a student from the list to view their 360° academic profile.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
