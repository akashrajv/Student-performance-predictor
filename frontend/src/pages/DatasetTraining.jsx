import React, { useState, useEffect } from 'react';
import {
  Database,
  Upload,
  Download,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Table,
  Layers,
  Cpu,
} from 'lucide-react';
import { apiService } from '../services/api';

export default function DatasetTraining() {
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [trainSummary, setTrainSummary] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadPreview();
  }, []);

  const loadPreview = async () => {
    try {
      const res = await apiService.previewDataset();
      setPreviewData(res);
    } catch (err) {
      console.error('Error loading dataset preview:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    setRetraining(true);
    setMessage(null);
    try {
      const res = await apiService.trainModels();
      setTrainSummary(res);
      setMessage({
        type: 'success',
        text: `Independently trained all ${res.models_evaluated?.length || 3} models on ${res.dataset_records} student records. Best model chosen: ${res.best_model} (Train Acc: ${(res.best_training_accuracy * 100).toFixed(2)}%)!`,
      });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.message || 'Model training failed',
      });
    } finally {
      setRetraining(false);
    }
  };

  const handleUploadAndTrain = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploadLoading(true);
    setMessage(null);

    try {
      const res = await apiService.uploadDataset(uploadFile);
      setMessage({
        type: 'success',
        text: res.message || 'Custom dataset uploaded and models retrained!',
      });
      loadPreview();
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.message || 'Dataset upload failed',
      });
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-5 h-5 text-indigo-400" />
            Dataset Management & ML Pipeline Retraining
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage student training records, inspect preprocessing schema, upload custom datasets, and trigger automated model retraining.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="/api/dataset/sample"
            download
            className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors inline-flex items-center gap-2 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span>Download CSV Template</span>
          </a>
          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${retraining ? 'animate-spin' : ''}`} />
            <span>{retraining ? 'Retraining Pipeline...' : 'Retrain All Models'}</span>
          </button>
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-xl text-xs flex items-center gap-3 ${
            message.type === 'success'
              ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-300'
              : 'bg-rose-500/15 border border-rose-500/30 text-rose-300'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Grid: Upload & Retrain Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Custom Dataset */}
        <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Upload className="w-4 h-4 text-purple-400" />
            Upload Custom Training Dataset
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Supply a custom educational dataset with student features (attendance, study hours, previous grade, assessment, etc.) and a target column <code className="text-indigo-300">Performance_Class</code>.
          </p>

          <form onSubmit={handleUploadAndTrain} className="space-y-3 pt-2">
            <label className="block border-2 border-dashed border-slate-700 hover:border-purple-500/60 rounded-xl p-4 text-center cursor-pointer transition-colors bg-slate-900/50">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setUploadFile(e.target.files[0])}
                className="hidden"
              />
              <div className="flex items-center justify-center gap-2 text-xs text-slate-300">
                <Upload className="w-4 h-4 text-purple-400" />
                <span>
                  {uploadFile ? (
                    <strong className="text-white">{uploadFile.name}</strong>
                  ) : (
                    'Click to upload new training CSV dataset'
                  )}
                </span>
              </div>
            </label>

            <button
              type="submit"
              disabled={uploadLoading || !uploadFile}
              className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-md shadow-purple-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <Sparkles className={`w-3.5 h-3.5 ${uploadLoading ? 'animate-spin' : ''}`} />
              <span>{uploadLoading ? 'Uploading & Fitting...' : 'Upload & Retrain Models'}</span>
            </button>
          </form>
        </div>

        {/* Retraining Metadata Card */}
        <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            ML Pipeline Architecture Summary
          </h3>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/50 border border-slate-800">
              <span className="text-slate-400">Total Benchmark Records:</span>
              <strong className="font-mono text-white">
                {previewData?.total_records || 1200} Students
              </strong>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/50 border border-slate-800">
              <span className="text-slate-400">Train / Test Split Ratio:</span>
              <strong className="font-mono text-white">
                80% Train (960) / 20% Test (240)
              </strong>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/50 border border-slate-800">
              <span className="text-slate-400">Target Feature:</span>
              <strong className="font-mono text-indigo-400">
                Performance_Class (High, Medium, Low)
              </strong>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/50 border border-slate-800">
              <span className="text-slate-400">Trained Model Artifacts:</span>
              <span className="text-emerald-400 font-mono font-semibold">
                LR (L2), RF, XGBoost (Best Model Selected)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Model Training Comparison Table if available */}
      {trainSummary?.comparison && (
        <div className="p-6 rounded-2xl glass-card border border-emerald-500/30 space-y-4 bg-emerald-950/10">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Latest Training Accuracy Benchmark & Model Selection
              </h3>
              <p className="text-xs text-slate-400">
                All models evaluated independently on training data; model with highest training accuracy designated as champion.
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/20 px-3 py-1 rounded-full border border-emerald-500/40">
              Champion: {trainSummary.best_model} ({(trainSummary.best_training_accuracy * 100).toFixed(2)}%)
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800">
                  <th className="py-2.5 px-3 font-semibold">Model</th>
                  <th className="py-2.5 px-3 font-semibold">Training Accuracy</th>
                  <th className="py-2.5 px-3 font-semibold">Test Accuracy</th>
                  <th className="py-2.5 px-3 font-semibold">F1-Score</th>
                  <th className="py-2.5 px-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {trainSummary.comparison.map((comp) => (
                  <tr
                    key={comp.model_name}
                    className={comp.is_best ? 'bg-emerald-950/30' : 'hover:bg-slate-800/30'}
                  >
                    <td className="py-2.5 px-3 font-sans font-semibold text-white">
                      {comp.model_name}
                    </td>
                    <td className="py-2.5 px-3 text-emerald-400 font-bold">
                      {(comp.train_accuracy * 100).toFixed(2)}%
                    </td>
                    <td className="py-2.5 px-3 text-indigo-400">
                      {(comp.test_accuracy * 100).toFixed(2)}%
                    </td>
                    <td className="py-2.5 px-3 text-purple-400">
                      {(comp.f1_score * 100).toFixed(2)}%
                    </td>
                    <td className="py-2.5 px-3 font-sans">
                      {comp.is_best ? (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                          ★ Best Model Selected
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">Alternative</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Dataset Preview Table */}
      <div className="p-6 rounded-2xl glass-card border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Table className="w-4 h-4 text-indigo-400" />
              Dataset Sample Records
            </h3>
            <p className="text-xs text-slate-400">
              Preview of active training dataset features and ground truth labels
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Showing first 10 rows
          </span>
        </div>

        {previewData?.preview ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800 bg-slate-900/60">
                  {previewData.columns.slice(0, 10).map((col) => (
                    <th key={col} className="py-2.5 px-3 font-semibold whitespace-nowrap">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {previewData.preview.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    {previewData.columns.slice(0, 10).map((col) => (
                      <td key={col} className="py-2.5 px-3 whitespace-nowrap text-slate-300">
                        {col === 'Performance_Class' || col === 'Performance_Level' ? (
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              ['High', 'Excellent', 'Good'].includes(row[col])
                                ? 'bg-emerald-500/20 text-emerald-300'
                                : ['Low', 'Poor'].includes(row[col])
                                ? 'bg-rose-500/20 text-rose-300'
                                : 'bg-amber-500/20 text-amber-300'
                            }`}
                          >
                            {row[col]}
                          </span>
                        ) : (
                          row[col]
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-slate-500">
            Loading preview data...
          </div>
        )}
      </div>
    </div>
  );
}
