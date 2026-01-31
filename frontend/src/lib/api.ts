import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; full_name: string; role: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

// Candidate API
export const candidateAPI = {
  getDashboard: () => api.get('/candidate/dashboard'),
  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/candidate/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getJobs: () => api.get('/candidate/jobs'),
  startAssessment: (jobId: number) => api.post('/candidate/assessment/start', { job_id: jobId }),
  getAssessmentQuestions: (assessmentId: number) =>
    api.get(`/candidate/assessment/${assessmentId}/questions`),
  getAssessmentStatus: (assessmentId: number) =>
    api.get(`/candidate/assessment/${assessmentId}/status`),
  completeAssessment: (assessmentId: number) =>
    api.post(`/candidate/assessment/${assessmentId}/complete`),
  getEvaluation: () => api.get('/candidate/evaluation'),
};

// Assessment API
export const assessmentAPI = {
  submitResponse: (data: {
    assessment_id: number;
    question_id: number;
    response_text?: string;
    selected_option?: number;
    slider_value?: number;
    time_taken_seconds: number;
  }) => api.post('/assessment/submit-response', data),
  executeCode: (data: { code: string; language: string; test_cases?: any[] }) =>
    api.post('/assessment/execute-code', data),
  getQuestion: (questionId: number) => api.get(`/assessment/question/${questionId}`),
};

// Proctoring API
export const proctoringAPI = {
  logEvent: (data: {
    assessment_id: number;
    event_type: string;
    severity: string;
    description: string;
  }) => api.post('/proctoring/event', data),
  getEvents: (assessmentId: number) => api.get(`/proctoring/events/${assessmentId}`),
  getSummary: (assessmentId: number) => api.get(`/proctoring/summary/${assessmentId}`),
};

// Recruiter API
export const recruiterAPI = {
  getDashboard: () => api.get('/recruiter/dashboard'),
  createJob: (data: any) => api.post('/recruiter/jobs', data),
  getJobs: () => api.get('/recruiter/jobs'),
  getJob: (jobId: number) => api.get(`/recruiter/jobs/${jobId}`),
  updateJob: (jobId: number, data: any) => api.put(`/recruiter/jobs/${jobId}`, data),
  deleteJob: (jobId: number) => api.delete(`/recruiter/jobs/${jobId}`),
  createQuestion: (data: any) => api.post('/recruiter/questions', data),
  getQuestions: (params?: any) => api.get('/recruiter/questions', { params }),
  getCandidates: (params?: any) => api.get('/recruiter/candidates', { params }),
  getCandidate: (candidateId: number) => api.get(`/recruiter/candidates/${candidateId}`),
  getShortlist: (jobId: number) => api.get(`/recruiter/candidates/job/${jobId}/shortlist`),
};

export default api;
