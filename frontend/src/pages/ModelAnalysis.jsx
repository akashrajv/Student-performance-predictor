import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Cpu,
  ShieldCheck,
  Zap,
  Layers,
  Award,
  BookOpen,
  RefreshCw,
  TrendingUp,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';
import { apiService } from '../services/api';
import ModelComparisonChart from '../charts/ModelComparisonChart';
import ConfusionMatrixChart from '../charts/ConfusionMatrixChart';
import FeatureImportanceChart from '../charts/FeatureImportanceChart';

export default function ModelAnalysis() {
  const [metrics, setMetrics] = useState({});
  const [bestModelName, setBestModelName] = useState('XGBoost');
  const [bestTrainAcc, setBestTrainAcc] = useState(0);
  const [comparisonList, setComparisonList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeModelKey, setActiveModelKey] = useState('XGBoost');
  const [activeImportanceModel, setActiveImportanceModel] = useState('XGBoost');

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const res = await apiService.getModelMetrics();
      const rawModels = res.models || {};
      // Filter out any legacy ensemble entries
      const filtered = {};
      Object.keys(rawModels).forEach((k) => {
        if (!k.toLowerCase().includes('ensemble')) {
          filtered[k] = rawModels[k];
        }
      });
      setMetrics(filtered);
      if (res.best_model) {
        setBestModelName(res.best_model);
      }
      if (res.best_training_accuracy) {
        setBestTrainAcc(res.best_training_accuracy);
      }
      if (res.comparison) {
        setComparisonList(res.comparison);
      }

      const keys = Object.keys(filtered);
      if (keys.length > 0) {
        const defaultKey = res.best_model && keys.includes(res.best_model) ? res.best_model : keys[0];
        setActiveModelKey(defaultKey);
        setActiveImportanceModel(defaultKey);
      }
    } catch (err) {
      console.error('Error loading metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
          <p className="text-sm text-slate-400">Loading Model Evaluation Metrics...</p>
        </div>
      </div>
    );
  }

  const modelArchitectures = [
    {
      id: 'Logistic Regression',
      title: 'Logistic Regression (L2 Regularized)',
      badge: 'Baseline / Linear',
      color: 'indigo',
      desc: 'Trained independently with L2 (Ridge) penalty to prevent overfitting on collinear student indicators (such as previous grades and attendance), establishing a stable and calibrated probabilistic baseline.',
      icon: Cpu,
    },
    {
      id: 'Random Forest',
      title: 'Random Forest Classifier',
      badge: 'Bagging Ensemble',
      color: 'purple',
      desc: 'Trained independently with 100 de-correlated decision trees to capture nonlinear synergies between study hours, sleep deprivation, and assignment completion without feature scale distortion.',
      icon: Layers,
    },
    {
      id: 'XGBoost',
      title: 'XGBoost (Extreme Gradient Boosting)',
      badge: 'Gradient Boosting',
      color: 'emerald',
      desc: 'Trained independently using gradient boosting with second-order tree pruning, delivering high predictive accuracy and resilient boundary detection for borderline at-risk cases.',
      icon: Zap,
    },
  ];

  const currentMatrixData = metrics[activeModelKey]?.confusion_matrix || [];
  const currentClasses = metrics[activeModelKey]?.classes || ['High', 'Medium', 'Low'];
  const currentImportances = metrics[activeImportanceModel]?.feature_importance || {};

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Page Title */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-400" />
          Independent Machine Learning Model Comparative Analysis
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Independent training of Logistic Regression (L2), Random Forest, and XGBoost on academic records. The system automatically benchmarks accuracy scores and designates the model with highest training accuracy as champion.
        </p>
      </div>

      {/* Selected Best Model Champion Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-indigo-950/30 to-slate-900 border border-emerald-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-lg shadow-emerald-950/20">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                Selected Champion Model
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Selection Metric: Best Training Accuracy
              </span>
            </div>
            <h3 className="text-base font-bold text-white mt-1 flex items-center gap-2">
              <span>{bestModelName}</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400 inline" />
            </h3>
            <p className="text-xs text-slate-300">
              Achieved the highest training accuracy of{' '}
              <strong className="text-emerald-400 font-mono">
                {(bestTrainAcc * 100).toFixed(2)}%
              </strong>{' '}
              among all independently trained candidates.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-slate-900/80 px-4 py-2.5 rounded-xl border border-slate-800 text-xs font-mono shrink-0">
          <div>
            <div className="text-[10px] text-slate-400">Train Accuracy</div>
            <div className="text-emerald-400 font-bold text-sm">
              {(bestTrainAcc * 100).toFixed(2)}%
            </div>
          </div>
          <div className="w-px h-8 bg-slate-800" />
          <div>
            <div className="text-[10px] text-slate-400">Test Accuracy</div>
            <div className="text-indigo-400 font-bold text-sm">
              {metrics[bestModelName]?.accuracy
                ? (metrics[bestModelName].accuracy * 100).toFixed(2) + '%'
                : 'N/A'}
            </div>
          </div>
          <div className="w-px h-8 bg-slate-800" />
          <div>
            <div className="text-[10px] text-slate-400">F1 Score</div>
            <div className="text-purple-400 font-bold text-sm">
              {metrics[bestModelName]?.f1_score
                ? (metrics[bestModelName].f1_score * 100).toFixed(2) + '%'
                : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Model Architectures from Presentation Spec */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {modelArchitectures.map((arch) => {
          const Icon = arch.icon;
          const currentM = metrics[arch.id] || metrics[arch.title];
          const isBest = arch.id === bestModelName;
          return (
            <div
              key={arch.id}
              className={`p-5 rounded-2xl glass-card border space-y-3 flex flex-col justify-between transition-all ${
                isBest
                  ? 'border-emerald-500/50 bg-emerald-950/10 shadow-lg shadow-emerald-950/20'
                  : 'border-slate-800'
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    isBest ? 'bg-emerald-500/20 text-emerald-400' : 'bg-indigo-500/15 text-indigo-400'
                  }`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex items-center gap-1.5">
                    {isBest && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                        ★ Best Model
                      </span>
                    )}
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {arch.badge}
                    </span>
                  </div>
                </div>
                <h4 className="text-xs font-bold text-white leading-tight">
                  {arch.title}
                </h4>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  {arch.desc}
                </p>
              </div>

              {currentM && (
                <div className="pt-3 border-t border-slate-800/80 space-y-1.5 text-xs font-mono">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Training Accuracy:</span>
                    <span className="text-emerald-400 font-bold">
                      {currentM.train_accuracy != null
                        ? Math.round(currentM.train_accuracy * 1000) / 10 + '%'
                        : Math.round((currentM.accuracy || 0) * 1000) / 10 + '%'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">Test Accuracy:</span>
                    <span className="text-indigo-400">
                      {Math.round((currentM.accuracy || 0) * 1000) / 10}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Comparative Metrics Table */}
      <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-400" />
              Comprehensive Model Accuracy & Performance Comparison
            </h3>
            <p className="text-xs text-slate-400">
              System benchmarks Training Accuracy against held-out Test Accuracy (20% partition, 240 unseen students)
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800">
                <th className="py-2.5 px-3 font-semibold">Model Architecture</th>
                <th className="py-2.5 px-3 font-semibold">Training Accuracy</th>
                <th className="py-2.5 px-3 font-semibold">Test Accuracy</th>
                <th className="py-2.5 px-3 font-semibold">Precision</th>
                <th className="py-2.5 px-3 font-semibold">Recall</th>
                <th className="py-2.5 px-3 font-semibold">F1-Score</th>
                <th className="py-2.5 px-3 font-semibold">ROC-AUC</th>
                <th className="py-2.5 px-3 font-semibold">Status</th>r
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {Object.keys(metrics).map((mName) => {
                const m = metrics[mName];
                const isBest = mName === bestModelName;
                const trainAcc = m.train_accuracy != null ? m.train_accuracy : m.accuracy;
                return (
                  <tr
                    key={mName}
                    className={`transition-colors ${
                      isBest ? 'bg-emerald-950/20 hover:bg-emerald-950/30' : 'hover:bg-slate-800/30'
                    }`}
                  >
                    <td className="py-3 px-3 font-sans font-semibold text-white flex items-center gap-2">
                      <span>{mName}</span>
                      {isBest && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    </td>
                    <td className="py-3 px-3 text-emerald-400 font-bold">
                      {(trainAcc * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-3 text-indigo-400 font-bold">
                      {(m.accuracy * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      {(m.precision * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      {(m.recall * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-3 text-purple-400 font-bold">
                      {(m.f1_score * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-3 text-cyan-400">
                      {m.roc_auc ? (m.roc_auc * 100).toFixed(2) + '%' : 'N/A'}
                    </td>
                    <td className="py-3 px-3 font-sans">
                      {isBest ? (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                          ★ Selected Best Model
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">
                          Candidate
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recharts Bar Chart */}
      <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            Model Accuracy Scores & Metric Comparison Chart
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Green indicates Training Accuracy (the selection metric), Indigo represents held-out Test Accuracy.
          </p>
        </div>
        <ModelComparisonChart metrics={metrics} />
      </div>

      {/* Grid: Confusion Matrix & Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix Section */}
        <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-100">
                Confusion Matrix
              </h3>
              <p className="text-xs text-slate-400">
                Predicted vs Actual class distributions
              </p>
            </div>
            {/* Model selector tabs */}
            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-[11px]">
              {Object.keys(metrics).map((k) => (
                <button
                  key={k}
                  onClick={() => setActiveModelKey(k)}
                  className={`px-2 py-1 rounded-lg transition-colors cursor-pointer ${
                    activeModelKey === k
                      ? 'bg-indigo-600 text-white font-semibold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {k.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          <ConfusionMatrixChart
            matrix={currentMatrixData}
            classes={currentClasses}
            modelName={activeModelKey}
          />
        </div>

        {/* Global Feature Importance Section */}
        <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-100">
                Global Feature Importance
              </h3>
              <p className="text-xs text-slate-400">
                Relative influence of student predictors
              </p>
            </div>
            {/* Model selector tabs */}
            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-[11px]">
              {Object.keys(metrics).map((k) => (
                <button
                  key={k}
                  onClick={() => setActiveImportanceModel(k)}
                  className={`px-2 py-1 rounded-lg transition-colors cursor-pointer ${
                    activeImportanceModel === k
                      ? 'bg-purple-600 text-white font-semibold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {k.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          <FeatureImportanceChart importances={currentImportances} />
        </div>
      </div>
    </div>
  );
}
