/**
 * Environment configuration for the frontend.
 * Uses Vite environment variables (VITE_ prefix).
 */

interface Config {
  apiBaseUrl: string;
  appName: string;
  appVersion: string;
  isDevelopment: boolean;
  isProduction: boolean;
}

export const config: Config = {
  // API Base URL from environment variable
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // App metadata
  appName: import.meta.env.VITE_APP_NAME || 'Feedback System',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // Environment flags
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

// Validate required environment variables
if (!config.apiBaseUrl) {
  console.error('VITE_API_BASE_URL environment variable is required');
  throw new Error('Missing required environment variable: VITE_API_BASE_URL');
}

// Log config in development (helps debugging)
if (config.isDevelopment) {
  console.log('🔧 Frontend Configuration:', {
    apiBaseUrl: config.apiBaseUrl,
    environment: config.isDevelopment ? 'development' : 'production',
  });
}

export default config;

