import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/v1';

const api = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (userData) => api.post('/auth/register', userData),
};

// Logs
export const logsAPI = {
  ingest: (logData) => api.post('/logs/ingest', logData),
  ingestBatch: (logs) => api.post('/logs/ingest/batch', { logs }),
  getAll: (params) => api.get('/logs', { params }),
  getById: (id) => api.get(`/logs/${id}`),
  getStats: (hours = 24) => api.get(`/logs/stats?hours=${hours}`),
};

// Alerts
export const alertsAPI = {
  getAll: (params) => api.get('/alerts', { params }),
  getById: (id) => api.get(`/alerts/${id}`),
  create: (alertData) => api.post('/alerts', alertData),
  update: (id, updateData) => api.patch(`/alerts/${id}`, updateData),
  acknowledge: (id) => api.post(`/alerts/${id}/acknowledge`),
  delete: (id) => api.delete(`/alerts/${id}`),
  getStats: (hours = 24) => api.get(`/alerts/stats?hours=${hours}`),
};

// Detection Rules
export const rulesAPI = {
  getAll: (params) => api.get('/rules', { params }),
  getById: (id) => api.get(`/rules/${id}`),
  create: (ruleData) => api.post('/rules', ruleData),
  update: (id, updateData) => api.patch(`/rules/${id}`, updateData),
  toggle: (id) => api.post(`/rules/${id}/toggle`),
  delete: (id) => api.delete(`/rules/${id}`),
};

// Incidents
export const incidentsAPI = {
  getAll: (params) => api.get('/incidents', { params }),
  getById: (incidentId) => api.get(`/incidents/${incidentId}`),
  create: (incidentData) => api.post('/incidents', incidentData),
  update: (incidentId, updateData) => api.patch(`/incidents/${incidentId}`, updateData),
  delete: (incidentId) => api.delete(`/incidents/${incidentId}`),
};

export default api;
