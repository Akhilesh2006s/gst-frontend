// API Configuration
// Use environment variable in production, localhost for development
const getApiBaseUrl = (): string => {
  // Check for environment variable first
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // In production, use Railway backend URL
  if (import.meta.env.PROD) {
    return 'https://web-production-f50e6.up.railway.app/api';
  }
  
  // Development: use Railway backend URL (or localhost if needed)
  return 'https://web-production-f50e6.up.railway.app/api';
};

const API_BASE_URL = getApiBaseUrl();

export default API_BASE_URL;

