import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import PredictPage from './pages/PredictPage';
import BatchPage from './pages/BatchPage';
import ModelAnalysis from './pages/ModelAnalysis';
import StudentDetails from './pages/StudentDetails';
import DatasetTraining from './pages/DatasetTraining';
import ResumeAnalyzer from './pages/ResumeAnalyzer';
import { apiService } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [modelsReady, setModelsReady] = useState(true);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await apiService.getHealth();
      setModelsReady(res.models_trained);
    } catch (err) {
      console.error('Backend health check error:', err);
      setModelsReady(false);
    }
  };

  const pageHeaders = {
    dashboard: {
      title: 'Academic Analytics Dashboard',
      subtitle: 'Overview of student performance metrics, risk distributions, and model performance',
    },
    predict: {
      title: 'Student Performance Prediction',
      subtitle: 'Individual academic inference with Explainable AI attribution & grounded LLM intervention',
    },
    batch: {
      title: 'Batch Cohort Prediction',
      subtitle: 'Upload CSV datasets for cohort-wide risk scoring and CSV export',
    },
    analysis: {
      title: 'Model Evaluation & Architecture',
      subtitle: 'Independent training and accuracy benchmarking of Logistic Regression (L2), Random Forest, and XGBoost',
    },
    students: {
      title: 'Student Academic Directory',
      subtitle: 'Comprehensive 360° student records, performance history, and action plans',
    },
    resume: {
      title: 'AI Resume Analyzer & Placement Readiness',
      subtitle: 'Deterministic skill matching against campus recruitment datasets and grounded AI career roadmaps',
    },
    dataset: {
      title: 'Dataset & Model Retraining',
      subtitle: 'Manage benchmark data, upload custom datasets, and execute automated training pipelines',
    },
  };

  const handleSelectStudent = (studentId) => {
    setSelectedStudentId(studentId);
    setActiveTab('students');
  };

  const handlePredictForStudent = (student) => {
    setActiveTab('predict');
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        modelsReady={modelsReady}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          title={pageHeaders[activeTab]?.title || 'Student Performance Predictor'}
          subtitle={pageHeaders[activeTab]?.subtitle}
          onQuickPredict={() => setActiveTab('predict')}
        />

        <main className="flex-1 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <Dashboard
              setActiveTab={setActiveTab}
              onSelectStudent={handleSelectStudent}
            />
          )}

          {activeTab === 'predict' && <PredictPage />}

          {activeTab === 'batch' && <BatchPage />}

          {activeTab === 'analysis' && <ModelAnalysis />}

          {activeTab === 'students' && (
            <StudentDetails
              initialStudentId={selectedStudentId}
              onPredictForStudent={handlePredictForStudent}
            />
          )}

          {activeTab === 'resume' && <ResumeAnalyzer />}

          {activeTab === 'dataset' && <DatasetTraining />}
        </main>
      </div>
    </div>
  );
}
