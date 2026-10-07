const API_BASE = '/api';

export async function fetchJson(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorDetail = 'Network request failed';
    try {
      const err = await res.json();
      errorDetail = err.detail || err.message || JSON.stringify(err);
    } catch (e) {
      errorDetail = res.statusText || `${res.status} Error`;
    }
    throw new Error(errorDetail);
  }

  return await res.json();
}

export const apiService = {
  // Health
  getHealth: () => fetchJson('/health'),

  // Models & Metrics
  getModels: () => fetchJson('/models'),
  getModelMetrics: () => fetchJson('/model-metrics'),

  // Predictions
  predictStudent: (studentData, modelName = 'XGBoost') =>
    fetchJson('/predict', {
      method: 'POST',
      body: JSON.stringify({
        student: studentData,
        model_name: modelName,
      }),
    }),

  batchPredict: async (file, modelName = 'XGBoost') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_name', modelName);

    const res = await fetch(`${API_BASE}/batch-predict`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Batch prediction failed');
    }
    return await res.json();
  },

  // LLM Explanation
  explainPrediction: (payload) =>
    fetchJson('/llm/explain', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Dashboard & Students
  getDashboardStats: () => fetchJson('/dashboard/stats'),
  getStudents: (limit = 100, search = '') =>
    fetchJson(`/students?limit=${limit}&search=${encodeURIComponent(search)}`),
  getStudentById: (id) => fetchJson(`/student/${encodeURIComponent(id)}`),

  // Dataset & Retraining
  previewDataset: () => fetchJson('/dataset/preview'),
  trainModels: () =>
    fetchJson('/train', {
      method: 'POST',
    }),
  uploadDataset: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/dataset/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Dataset upload failed');
    }
    return await res.json();
  },

  // AI Resume Analyzer & Placement Readiness
  analyzeResume: async (file, studentId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (studentId) {
      formData.append('student_id', studentId);
    }

    const res = await fetch(`${API_BASE}/resume/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Resume analysis failed');
    }
    return await res.json();
  },
  getRecruitmentMarket: () => fetchJson('/resume/recruitment-market'),
  getResumeHistory: (limit = 10) => fetchJson(`/resume/history?limit=${limit}`),
  getStudentCombinedProfile: (studentId) =>
    fetchJson(`/resume/student/${encodeURIComponent(studentId)}/profile`),
};
