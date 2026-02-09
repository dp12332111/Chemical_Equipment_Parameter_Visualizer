import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',  // backend port
});

// authentication interceptor for Basic Auth (matches your Django backend)
api.interceptors.request.use(config => {
  const username = localStorage.getItem('username');
  const password = localStorage.getItem('password');
  if (username && password) {
    const token = btoa(`${username}:${password}`);
    config.headers.Authorization = `Basic ${token}`;
  }
  return config;
});

// Upload CSV (multipart form data, no auth required per your backend)
export const uploadCSV = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }  // only for upload
  });
};

export const getSummary = () => api.get('summary/');

export const getHistory = () => api.get('history/');

// For PDF
export const getPDF = () => api.get('pdf/', { responseType: 'blob' });