import React, { useState } from 'react';
import {
  Sparkles,
  UserCheck,
  Cpu,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  ArrowRight,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import { apiService } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import FactorBreakdown from '../components/FactorBreakdown';
import LLMExplanationCard from '../components/LLMExplanationCard';
import ModelConsensusCard from '../components/ModelConsensusCard';

const PRESETS = {
  at_risk: {
    student_id: 'STU-RISK-201',
    name: 'Rohan Sharma',
    attendance_percentage: 54.0,
    study_hours_per_week: 6.0,
    previous_grade: 52.0,
    assignment_score: 48.0,
    assessment_score: 45.0,
    participation_score: 40.0,
    sleep_hours: 5.5,
    tutoring_sessions: 0,
    extracurricular_activities: 'No',
    parental_education: 'High School',
    internet_access: 'No',
  },
  average: {
    student_id: 'STU-AVG-305',
    name: 'Kavya Patel',
    attendance_percentage: 78.0,
    study_hours_per_week: 16.0,
    previous_grade: 72.0,
    assignment_score: 70.0,
    assessment_score: 68.0,
    participation_score: 74.0,
    sleep_hours: 7.0,
    tutoring_sessions: 1,
    extracurricular_activities: 'Yes',
    parental_education: 'Bachelor',
    internet_access: 'Yes',
  },
  high_performer: {
    student_id: 'STU-TOP-409',
    name: 'Akashraj Sundaram',
    attendance_percentage: 95.0,
    study_hours_per_week: 28.0,
    previous_grade: 92.0,
    assignment_score: 94.0,
    assessment_score: 91.0,
    participation_score: 88.0,
    sleep_hours: 7.5,
    tutoring_sessions: 3,
    extracurricular_activities: 'Yes',
    parental_education: 'Master',
    internet_access: 'Yes',
  },
};

export default function PredictPage() {
  const [formData, setFormData] = useState(PRESETS.at_risk);
  const [selectedModel, setSelectedModel] = useState('Best Model');
  const [bestModelName, setBestModelName] = useState('');
  const [loading, setLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [llmResult, setLlmResult] = useState(null);
  const [llmLoading, setLlmLoading] = useState(false);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    apiService.getModels().then((res) => {
      if (res?.best_model) {
        setBestModelName(res.best_model);
      }
    }).catch(() => {});
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        ['tutoring_sessions'].includes(name)
          ? parseInt(value) || 0
          : [
              'attendance_percentage',
              'study_hours_per_week',
              'previous_grade',
              'assignment_score',
              'assessment_score',
              'participation_score',
              'sleep_hours',
            ].includes(name)
          ? parseFloat(value) || 0
          : value,
    }));
  };

  const handlePreset = (key) => {
    setFormData(PRESETS[key]);
    setPredictionResult(null);
    setLlmResult(null);
    setError(null);
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setLlmResult(null);

    try {
      const res = await apiService.predictStudent(formData, selectedModel);
      setPredictionResult(res);
    } catch (err) {
      setError(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateLLM = async () => {
    if (!predictionResult) return;
    setLlmLoading(true);
    try {
      const payload = {
        student_id: predictionResult.student_id,
        student_name: predictionResult.student_name,
        input_data: formData,
        predicted_class: predictionResult.predicted_class,
        confidence: predictionResult.confidence,
        risk_category: predictionResult.risk_category,
        risk_score: predictionResult.risk_score,
        contributing_factors: predictionResult.contributing_factors,
        prediction_id: predictionResult.prediction_id,
        consensus: predictionResult.consensus,
      };
      const res = await apiService.explainPrediction(payload);
      setLlmResult(res);
    } catch (err) {
      console.error('LLM generation error:', err);
    } finally {
      setLlmLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-indigo-400" />
            Individual Student Performance Prediction
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Input student academic & behavioral metrics to predict academic outcomes and compute Explainable AI factor attribution.
          </p>
        </div>

        {/* Quick Demo Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 mr-1">Load Demo Case:</span>
          <button
            type="button"
            onClick={() => handlePreset('at_risk')}
            className="px-2.5 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs border border-rose-500/30 transition-colors cursor-pointer"
          >
            At-Risk Student
          </button>
          <button
            type="button"
            onClick={() => handlePreset('average')}
            className="px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 text-xs border border-amber-500/30 transition-colors cursor-pointer"
          >
            Average Student
          </button>
          <button
            type="button"
            onClick={() => handlePreset('high_performer')}
            className="px-2.5 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-xs border border-emerald-500/30 transition-colors cursor-pointer"
          >
            High Performer
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid: Form on Left, Results on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Column */}
        <div className="lg:col-span-5 space-y-6">
          <form
            onSubmit={handlePredict}
            className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <span>Student Academic Profile</span>
              </h3>
              {/* Model Choice */}
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] text-slate-400">Model:</span>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1 focus:ring-1 focus:ring-indigo-500 outline-none"
                >
                  <option value="Model Consensus">
                    Model Consensus (Multi-Model Agreement)
                  </option>
                  <option value="Best Model">
                    Best Model {bestModelName ? `(${bestModelName} - Recommended)` : '(Auto-selected)'}
                  </option>
                  <option value="XGBoost">XGBoost Classifier</option>
                  <option value="Random Forest">Random Forest Classifier</option>
                  <option value="Logistic Regression">Logistic Regression (L2 Regularized)</option>
                </select>
              </div>
            </div>

            {/* Identifiers */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Student ID
                </label>
                <input
                  type="text"
                  name="student_id"
                  value={formData.student_id}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none"
                />
              </div>
            </div>

            {/* Academic Core Features */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Attendance Rate (%)
                </label>
                <input
                  type="number"
                  name="attendance_percentage"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.attendance_percentage}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Study Hours / Week
                </label>
                <input
                  type="number"
                  name="study_hours_per_week"
                  min="0"
                  max="80"
                  step="0.5"
                  value={formData.study_hours_per_week}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Previous Grade (0-100)
                </label>
                <input
                  type="number"
                  name="previous_grade"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.previous_grade}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Assignment Score (0-100)
                </label>
                <input
                  type="number"
                  name="assignment_score"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.assignment_score}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Assessment / Midterm (0-100)
                </label>
                <input
                  type="number"
                  name="assessment_score"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.assessment_score}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Class Participation (0-100)
                </label>
                <input
                  type="number"
                  name="participation_score"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.participation_score}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
            </div>

            {/* Behavioral and Demographic Features */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Sleep Hours / Night
                </label>
                <input
                  type="number"
                  name="sleep_hours"
                  min="3"
                  max="14"
                  step="0.5"
                  value={formData.sleep_hours}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Tutoring Sessions / Mo
                </label>
                <input
                  type="number"
                  name="tutoring_sessions"
                  min="0"
                  max="15"
                  value={formData.tutoring_sessions}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-500 outline-none font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-[10px] font-semibold text-slate-400 mb-1">
                  Extracurricular
                </label>
                <select
                  name="extracurricular_activities"
                  value={formData.extracurricular_activities}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-2 py-2 text-xs text-white focus:border-indigo-500 outline-none"
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-slate-400 mb-1">
                  Parent Education
                </label>
                <select
                  name="parental_education"
                  value={formData.parental_education}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-2 py-2 text-xs text-white focus:border-indigo-500 outline-none"
                >
                  <option value="High School">High School</option>
                  <option value="Bachelor">Bachelor</option>
                  <option value="Master">Master</option>
                  <option value="Doctorate">Doctorate</option>
                </select>
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-slate-400 mb-1">
                  Internet Access
                </label>
                <select
                  name="internet_access"
                  value={formData.internet_access}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-2 py-2 text-xs text-white focus:border-indigo-500 outline-none"
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Evaluating Features...' : 'Predict Performance'}</span>
            </button>
          </form>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-7 space-y-6">
          {predictionResult ? (
            <div className="space-y-6">
              {/* Model Consensus Card */}
              {predictionResult.consensus && (
                <ModelConsensusCard consensus={predictionResult.consensus} />
              )}

              {/* Primary Prediction Card */}
              <div className="p-6 rounded-2xl glass-card border border-indigo-500/30 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                  <div>
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Student: {predictionResult.student_name} ({predictionResult.student_id})
                    </span>
                    <h3 className="text-xl font-black text-white mt-0.5">
                      Predicted: {predictionResult.predicted_class} Academic Outcome
                    </h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <RiskBadge risk={predictionResult.risk_category} size="lg" />
                  </div>
                </div>

                {/* Score Meters Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-[11px] text-slate-400 font-semibold uppercase">
                      Risk Index
                    </div>
                    <div className={`text-2xl font-black mt-1 ${
                      predictionResult.risk_score >= 50 ? 'text-rose-400' :
                      predictionResult.risk_score >= 25 ? 'text-amber-400' : 'text-emerald-400'
                    }`}>
                      {predictionResult.risk_score}%
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      Derived failure probability
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-[11px] text-slate-400 font-semibold uppercase">
                      Model Confidence
                    </div>
                    <div className="text-2xl font-black text-indigo-400 mt-1">
                      {Math.round(predictionResult.confidence * 100)}%
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {predictionResult.model_used}
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-[11px] text-slate-400 font-semibold uppercase">
                      Status Level
                    </div>
                    <div className="text-sm font-bold text-white mt-2">
                      {predictionResult.risk_category}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      Immediate action recommended
                    </div>
                  </div>
                </div>

                {/* Class Probabilities Bar */}
                <div className="space-y-2 pt-2">
                  <div className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                    <span>Class Probability Distribution:</span>
                    <span className="font-mono text-[11px] text-slate-400">
                      High: {Math.round((predictionResult.probabilities?.High || 0) * 100)}% •
                      Medium: {Math.round((predictionResult.probabilities?.Medium || 0) * 100)}% •
                      Low: {Math.round((predictionResult.probabilities?.Low || 0) * 100)}%
                    </span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-slate-800 overflow-hidden flex">
                    <div
                      style={{ width: `${(predictionResult.probabilities?.High || 0) * 100}%` }}
                      className="bg-emerald-500 h-full transition-all duration-500"
                      title="High Performance"
                    />
                    <div
                      style={{ width: `${(predictionResult.probabilities?.Medium || 0) * 100}%` }}
                      className="bg-amber-500 h-full transition-all duration-500"
                      title="Medium Performance"
                    />
                    <div
                      style={{ width: `${(predictionResult.probabilities?.Low || 0) * 100}%` }}
                      className="bg-rose-500 h-full transition-all duration-500"
                      title="Low (At-Risk) Performance"
                    />
                  </div>
                </div>
              </div>

              {/* Explainable AI Attribution */}
              <div className="p-6 rounded-2xl glass-card border border-slate-800">
                <FactorBreakdown
                  factors={predictionResult.contributing_factors}
                  predictedClass={predictionResult.predicted_class}
                  riskCategory={predictionResult.risk_category}
                />
              </div>

              {/* LLM Explanation & Recommendations */}
              <LLMExplanationCard
                explanationData={llmResult}
                loading={llmLoading}
                onGenerate={handleGenerateLLM}
              />
            </div>
          ) : (
            <div className="p-12 rounded-2xl glass-card border border-dashed border-slate-800 text-center flex flex-col items-center justify-center min-h-[400px] space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Sparkles className="w-8 h-8" />
              </div>
              <div className="max-w-md">
                <h3 className="text-base font-bold text-slate-200">
                  Ready for Performance Prediction
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Enter student details on the left or select a preset, then click "Predict Performance" to generate ML predictions, XAI factor attributions, and AI recommendations.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
