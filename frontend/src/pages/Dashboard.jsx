import React, { useState, useEffect } from 'react';
import {
  Users,
  ShieldAlert,
  GraduationCap,
  CalendarCheck,
  TrendingUp,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Cpu,
  FileSpreadsheet,
} from 'lucide-react';
import { apiService } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import ModelComparisonChart from '../charts/ModelComparisonChart';
import RiskDistributionChart from '../charts/RiskDistributionChart';

export default function Dashboard({ setActiveTab, onSelectStudent }) {
  const [stats, setStats] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [statsData, metricsData] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getModelMetrics().catch(() => ({ models: {} })),
      ]);
      setStats(statsData);
      setMetrics(metricsData.models || {});
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
          <p className="text-sm text-slate-400">Loading Academic Analytics...</p>
        </div>
      </div>
    );
  }

  const kpis = [
    {
      label: 'Total Students',
      value: stats?.total_students_in_db || 0,
      icon: Users,
      color: 'indigo',
      sub: 'Enrolled in academic database',
    },
    {
      label: 'Students At Risk',
      value: stats?.high_risk_count || 0,
      icon: ShieldAlert,
      color: 'rose',
      sub: `${stats?.moderate_risk_count || 0} moderate risk flagged`,
      highlight: true,
    },
    {
      label: 'Average Attendance',
      value: `${stats?.avg_attendance || 0}%`,
      icon: CalendarCheck,
      color: 'emerald',
      sub: 'Cohort attendance benchmark',
    },
    {
      label: 'Avg Risk Index',
      value: `${stats?.avg_predicted_risk || 0}%`,
      icon: TrendingUp,
      color: 'amber',
      sub: 'Mean probability score of failure',
    },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner / Hero */}
      <div className="rounded-2xl bg-gradient-to-r from-indigo-900/60 via-slate-900/80 to-purple-900/40 border border-indigo-500/25 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 backdrop-blur-md relative overflow-hidden">
        <div className="space-y-1.5 z-10">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Multi-Model Academic Intelligence
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Academic Early Warning & Intervention Platform
          </h2>
          <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
            Comparing Logistic Regression (L2), Random Forest, and XGBoost with Explainable AI and grounded LLM recommendations for early academic support.
          </p>
        </div>

        <div className="flex items-center gap-2.5 z-10">
          <button
            onClick={handleRefresh}
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs transition-colors cursor-pointer"
            title="Refresh Dashboard"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setActiveTab('predict')}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all cursor-pointer flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Predict Student</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className={`p-5 rounded-2xl glass-card glass-card-hover border ${
                kpi.highlight
                  ? 'border-rose-500/30 bg-rose-500/5'
                  : 'border-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">
                  {kpi.label}
                </span>
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                    kpi.color === 'rose'
                      ? 'bg-rose-500/15 text-rose-400'
                      : kpi.color === 'emerald'
                      ? 'bg-emerald-500/15 text-emerald-400'
                      : kpi.color === 'amber'
                      ? 'bg-amber-500/15 text-amber-400'
                      : 'bg-indigo-500/15 text-indigo-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="text-2xl font-black text-white mt-2">
                {kpi.value}
              </div>
              <div className="text-[11px] text-slate-400 mt-1">
                {kpi.sub}
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model Accuracy Comparison */}
        <div className="lg:col-span-2 p-5 rounded-2xl glass-card border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" />
                Multi-Model Performance Comparison
              </h3>
              <p className="text-xs text-slate-400">
                Training Accuracy & Test metrics across independently trained models (LR L2, RF, XGBoost)
              </p>
            </div>
            <button
              onClick={() => setActiveTab('analysis')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 cursor-pointer"
            >
              Deep Analysis <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <ModelComparisonChart metrics={metrics} />
        </div>

        {/* Risk Distribution */}
        <div className="p-5 rounded-2xl glass-card border border-slate-800 space-y-3">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              Cohort Risk Distribution
            </h3>
            <p className="text-xs text-slate-400">
              Low Risk vs Moderate Risk vs High Risk
            </p>
          </div>
          <RiskDistributionChart riskDistribution={stats?.risk_distribution} />
        </div>
      </div>

      {/* Quick Launchpad & Recent Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Predictions */}
        <div className="lg:col-span-2 p-5 rounded-2xl glass-card border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-100">
                Recent Student Predictions
              </h3>
              <p className="text-xs text-slate-400">
                Latest evaluations logged to the database
              </p>
            </div>
            <button
              onClick={() => setActiveTab('students')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 cursor-pointer"
            >
              View All Directory <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {stats?.recent_predictions && stats.recent_predictions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-800/80">
                    <th className="pb-2 font-semibold">Student ID</th>
                    <th className="pb-2 font-semibold">Name</th>
                    <th className="pb-2 font-semibold">Model</th>
                    <th className="pb-2 font-semibold">Predicted Class</th>
                    <th className="pb-2 font-semibold">Risk Category</th>
                    <th className="pb-2 font-semibold">Risk Score</th>
                    <th className="pb-2 font-semibold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {stats.recent_predictions.map((p) => (
                    <tr
                      key={p.id}
                      className="hover:bg-slate-800/30 transition-colors"
                    >
                      <td className="py-2.5 font-mono text-slate-300">
                        {p.student_id}
                      </td>
                      <td className="py-2.5 font-medium text-white">
                        {p.student_name}
                      </td>
                      <td className="py-2.5 text-slate-400">
                        {p.model_used}
                      </td>
                      <td className="py-2.5">
                        <span className="font-semibold text-slate-200">
                          {p.predicted_class}
                        </span>
                      </td>
                      <td className="py-2.5">
                        <RiskBadge risk={p.risk_category} size="sm" />
                      </td>
                      <td className="py-2.5 font-mono text-slate-300">
                        {p.risk_score}%
                      </td>
                      <td className="py-2.5 text-right">
                        <button
                          onClick={() => {
                            if (onSelectStudent) onSelectStudent(p.student_id);
                            setActiveTab('students');
                          }}
                          className="text-xs text-indigo-400 hover:text-indigo-300 font-medium cursor-pointer"
                        >
                          Details →
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-slate-500">
              No recent predictions logged yet. Try predicting a student!
            </div>
          )}
        </div>

        {/* Quick Workflow Cards */}
        <div className="space-y-4">
          <div
            onClick={() => setActiveTab('batch')}
            className="p-5 rounded-2xl glass-card glass-card-hover border border-slate-800 cursor-pointer space-y-2 group"
          >
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 text-purple-400 flex items-center justify-center group-hover:scale-105 transition-transform">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-100 group-hover:text-purple-300 transition-colors">
              Batch CSV Scoring
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload a cohort CSV file to predict risk levels for multiple students at once and export reports.
            </p>
          </div>

          <div
            onClick={() => setActiveTab('dataset')}
            className="p-5 rounded-2xl glass-card glass-card-hover border border-slate-800 cursor-pointer space-y-2 group"
          >
            <div className="w-10 h-10 rounded-xl bg-indigo-500/15 text-indigo-400 flex items-center justify-center group-hover:scale-105 transition-transform">
              <Cpu className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
              Retrain & Tune Models
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Inspect training dataset, trigger new training iterations, and update ML model artifacts.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
