// API Configuration
// Use environment variable in production, localhost for development
const getApiBaseUrl = (): string => {
  // In production, use environment variable or relative path
  if (import.meta.env.PROD) {
    // Use relative path in production (same domain)
    return '/api';
  }
  
  // Development: use localhost
  return import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
};

const API_BASE_URL = getApiBaseUrl();

export default API_BASE_URL;

