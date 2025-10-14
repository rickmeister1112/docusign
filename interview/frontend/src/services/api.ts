import axios from "axios";
import type {
  Feedback,
  FeedbackCreate,
  FeedbackUpdate,
  UpvoteResponse,
} from "../types/feedback";

// API base URL - FastAPI server
const API_BASE_URL = "http://localhost:8000";

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Feedback API service
export const feedbackApi = {
  // Get all feedback entries
  getAll: async (): Promise<Feedback[]> => {
    const response = await api.get("/feedback/");
    return response.data;
  },

  // Get user's own feedback entries
  getMyFeedback: async (): Promise<Feedback[]> => {
    const response = await api.get("/feedback/my");
    return response.data;
  },

  // Get a single feedback entry by ID
  getById: async (id: number): Promise<Feedback> => {
    const response = await api.get(`/feedback/${id}`);
    return response.data;
  },

  // Create a new feedback entry
  create: async (feedback: FeedbackCreate): Promise<Feedback> => {
    const response = await api.post("/feedback/", feedback);
    return response.data;
  },

  // Update an existing feedback entry
  update: async (id: number, feedback: FeedbackUpdate): Promise<Feedback> => {
    const response = await api.put(`/feedback/${id}`, feedback);
    return response.data;
  },

  // Delete a feedback entry
  delete: async (id: number): Promise<void> => {
    await api.delete(`/feedback/${id}`);
  },

  // Upvote a feedback entry
  upvote: async (id: number): Promise<UpvoteResponse> => {
    const response = await api.post(`/feedback/${id}/upvote`);
    return response.data;
  },
};

export default api;
