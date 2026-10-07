import React, { useState } from 'react';
import {
  FileSpreadsheet,
  Upload,
  Download,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Search,
  Filter,
  RefreshCw,
  FileCheck,
} from 'lucide-react';
import { apiService } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export default function BatchPage() {
  const [file, setFile] = useState(null);
  const [selectedModel, setSelectedModel] = useState('Best Model');
  const [loading, setLoading] = useState(false);
  const [batchResult, setBatchResult] = useState(null);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleRunBatch = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select or upload a CSV file first.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await apiService.batchPredict(file, selectedModel);
      setBatchResult(res);
    } catch (err) {
      setError(err.message || 'Batch prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (!batchResult || !batchResult.predictions) return;

    const headers = [
      'Student ID',
      'Student Name',
      'LR Prediction',
      'RF Prediction',
      'XGBoost Prediction',
      'Final Prediction',
      'Consensus Count',
      'Consensus Percentage',
      'Average Confidence',
      'Predicted Class',
      'Risk Category',
      'Risk Score',
    ];

    const rows = batchResult.predictions.map((p) => {
      const c = p.consensus || {};
      const mp = c.model_predictions || {};
      return [
        p.student_id,
        `"${p.student_name}"`,
        `"${mp['Logistic Regression']?.prediction || 'N/A'}"`,
        `"${mp['Random Forest']?.prediction || 'N/A'}"`,
        `"${mp['XGBoost']?.prediction || 'N/A'}"`,
        `"${c.final_prediction || p.risk_category}"`,
        `"${c.models_agree_display || 'N/A'}"`,
        `"${c.consensus_percentage ? `${c.consensus_percentage}%` : 'N/A'}"`,
        `"${c.average_confidence_display || 'Confidence unavailable'}"`,
        p.predicted_class,
        p.risk_category,
        p.risk_score,
      ];
    });

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `predictions_${selectedModel.toLowerCase().replace(/ /g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Filter predictions
  const filteredPredictions = (batchResult?.predictions || []).filter((p) => {
    const matchesSearch =
      p.student_id.toLowerCase().includes(search.toLowerCase()) ||
      p.student_name.toLowerCase().includes(search.toLowerCase());

    const matchesRisk =
      riskFilter === 'ALL' ||
      p.risk_category.toLowerCase().includes(riskFilter.toLowerCase());

    return matchesSearch && matchesRisk;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-purple-400" />
            Batch Student Performance Prediction
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Upload cohort student data in CSV format to run predictions, identify at-risk students, and export reports.
          </p>
        </div>

        <a
          href="/api/dataset/sample"
          download
          className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors inline-flex items-center gap-2 cursor-pointer"
        >
          <Download className="w-3.5 h-3.5 text-indigo-400" />
          <span>Download Sample CSV Template</span>
        </a>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload & Configuration Card */}
      <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
        <form onSubmit={handleRunBatch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Select Cohort CSV File
              </label>
              <div className="flex items-center gap-3">
                <label className="flex-1 border-2 border-dashed border-slate-700 hover:border-indigo-500/60 rounded-xl p-4 text-center cursor-pointer transition-colors bg-slate-900/50">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <div className="flex items-center justify-center gap-2 text-xs text-slate-300">
                    <Upload className="w-4 h-4 text-indigo-400" />
                    <span>
                      {file ? (
                        <strong className="text-white">{file.name}</strong>
                      ) : (
                        'Click to browse or drop CSV file here'
                      )}
                    </span>
                  </div>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Target Model
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-3 focus:ring-1 focus:ring-indigo-500 outline-none"
              >
                <option value="Model Consensus">Model Consensus (Multi-Model Agreement)</option>
                <option value="Best Model">Best Model (Auto-selected by Training Accuracy)</option>
                <option value="XGBoost">XGBoost Classifier</option>
                <option value="Random Forest">Random Forest Classifier</option>
                <option value="Logistic Regression">Logistic Regression (L2 Regularized)</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={loading || !file}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-purple-600/30 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Processing Batch...' : 'Predict Cohort Performance'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Batch Results View */}
      {batchResult && (
        <div className="space-y-6">
          {/* Summary KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl glass-card border border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">
                Total Scored
              </span>
              <div className="text-2xl font-black text-white mt-1">
                {batchResult.total_students}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Model: {batchResult.model_used}
              </div>
            </div>

            <div className="p-4 rounded-xl glass-card border border-rose-500/25 bg-rose-500/5">
              <span className="text-[11px] font-semibold text-rose-300 uppercase">
                High Risk
              </span>
              <div className="text-2xl font-black text-rose-400 mt-1">
                {batchResult.risk_distribution['High Risk'] || 0}
              </div>
              <div className="text-[10px] text-rose-300 mt-0.5">
                Urgent academic intervention
              </div>
            </div>

            <div className="p-4 rounded-xl glass-card border border-amber-500/25 bg-amber-500/5">
              <span className="text-[11px] font-semibold text-amber-300 uppercase">
                Moderate Risk
              </span>
              <div className="text-2xl font-black text-amber-400 mt-1">
                {batchResult.risk_distribution['Moderate Risk'] || 0}
              </div>
              <div className="text-[10px] text-amber-300 mt-0.5">
                Needs monitoring & support
              </div>
            </div>

            <div className="p-4 rounded-xl glass-card border border-emerald-500/25 bg-emerald-500/5">
              <span className="text-[11px] font-semibold text-emerald-300 uppercase">
                Low Risk
              </span>
              <div className="text-2xl font-black text-emerald-400 mt-1">
                {batchResult.risk_distribution['Low Risk'] || 0}
              </div>
              <div className="text-[10px] text-emerald-300 mt-0.5">
                On track for high distinction
              </div>
            </div>
          </div>

          {/* Table Header Controls */}
          <div className="p-5 rounded-2xl glass-card border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-3">
                {/* Search */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search student ID or name..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:border-indigo-500 outline-none w-56"
                  />
                </div>

                {/* Risk Filter */}
                <div className="flex items-center gap-1.5 text-xs">
                  <Filter className="w-3.5 h-3.5 text-slate-400" />
                  {['ALL', 'High', 'Moderate', 'Low'].map((r) => (
                    <button
                      key={r}
                      onClick={() => setRiskFilter(r)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                        riskFilter === r
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      {r === 'ALL' ? 'All Risks' : `${r} Risk`}
                    </button>
                  ))}
                </div>
              </div>

              {/* Export Button */}
              <button
                onClick={handleExportCSV}
                className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors inline-flex items-center gap-2 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5 text-purple-400" />
                <span>Export Predictions CSV</span>
              </button>
            </div>

            {/* Results Table */}
            <div className="overflow-x-auto max-h-[500px]">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="sticky top-0 bg-slate-900 border-b border-slate-800 z-10">
                  <tr className="text-slate-400">
                    <th className="py-2.5 px-3 font-semibold">Student ID</th>
                    <th className="py-2.5 px-3 font-semibold">Name</th>
                    <th className="py-2.5 px-3 font-semibold">LR</th>
                    <th className="py-2.5 px-3 font-semibold">RF</th>
                    <th className="py-2.5 px-3 font-semibold">XGB</th>
                    <th className="py-2.5 px-3 font-semibold">Final Prediction</th>
                    <th className="py-2.5 px-3 font-semibold">Consensus</th>
                    <th className="py-2.5 px-3 font-semibold">Avg Conf</th>
                    <th className="py-2.5 px-3 font-semibold">Risk Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredPredictions.map((p, idx) => {
                    const c = p.consensus || {};
                    const mp = c.model_predictions || {};
                    return (
                      <tr
                        key={idx}
                        className="hover:bg-slate-800/40 transition-colors"
                      >
                        <td className="py-2.5 px-3 font-mono text-slate-300">
                          {p.student_id}
                        </td>
                        <td className="py-2.5 px-3 font-medium text-white">
                          {p.student_name}
                        </td>
                        <td className="py-2.5 px-3 text-[11px] text-slate-300">
                          {mp['Logistic Regression']?.prediction || 'N/A'}
                        </td>
                        <td className="py-2.5 px-3 text-[11px] text-slate-300">
                          {mp['Random Forest']?.prediction || 'N/A'}
                        </td>
                        <td className="py-2.5 px-3 text-[11px] text-slate-300">
                          {mp['XGBoost']?.prediction || 'N/A'}
                        </td>
                        <td className="py-2.5 px-3">
                          <RiskBadge risk={c.final_prediction || p.risk_category} size="sm" />
                        </td>
                        <td className="py-2.5 px-3 text-purple-300 font-mono">
                          {c.models_agree_display ? `${c.models_agree_display} (${c.consensus_percentage}%)` : 'N/A'}
                        </td>
                        <td className="py-2.5 px-3 text-emerald-300 font-mono">
                          {c.average_confidence_display || 'N/A'}
                        </td>
                        <td className="py-2.5 px-3 font-mono text-slate-300">
                          {p.risk_score}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
