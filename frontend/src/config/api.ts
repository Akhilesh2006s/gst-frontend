// API Configuration
// Use environment variable in production, localhost for development
const getApiBaseUrl = (): string => {
  // Check for environment variable first
  if (import.meta.env.VITE_API_URL) {
    const url = import.meta.env.VITE_API_URL;
    // Ensure no trailing slash and use HTTPS
    return url.replace(/\/$/, '').replace(/^http:/, 'https:');
  }
  
  // Always use HTTPS Railway backend URL
  const baseUrl = 'https://web-production-f50e6.up.railway.app/api';
  // Ensure no trailing slash
  return baseUrl.replace(/\/$/, '');
};

const API_BASE_URL = getApiBaseUrl();

export default API_BASE_URL;

