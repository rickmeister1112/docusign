import type { User, UserCreate, UserLogin, Token } from "../types/feedback";
import { config } from "../config/env";
import { storage } from "../utils/storage";
import { tokenManager } from "../utils/tokenManager";

const API_BASE_URL = config.apiBaseUrl;

class AuthService {
  private token: string | null = null;

  constructor() {
    // Load token from storage on initialization
    this.token = storage.getItem("auth_token");
    
    // Set up token expiry handling
    this.setupTokenExpiryHandling();
  }

  private setupTokenExpiryHandling(): void {
    // Handle token expiry
    tokenManager.setOnTokenExpiry(() => {
      this.logout();
    });

    // Handle token refresh (for now, just logout - can be enhanced later)
    tokenManager.setOnTokenRefresh(async () => {
      // TODO: Implement token refresh endpoint on backend
      // For now, return false to trigger logout
      return false;
    });

    // Start monitoring if we have a token
    if (this.token) {
      tokenManager.startMonitoring(this.token);
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async register(userData: UserCreate): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Registration failed");
    }

    return response.json();
  }

  async login(credentials: UserLogin): Promise<Token> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Login failed");
    }

    const tokenData = await response.json();
    this.setToken(tokenData.access_token);
    return tokenData;
  }

  async getCurrentUser(): Promise<User> {
    if (!this.token) {
      throw new Error("No authentication token");
    }

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.logout();
      }
      throw new Error("Failed to get current user");
    }

    return response.json();
  }

  logout(): void {
    this.token = null;
    storage.removeItem("auth_token");
    
    // Stop token monitoring
    tokenManager.stopMonitoring();
  }

  setToken(token: string): void {
    this.token = token;
    storage.setItem("auth_token", token);
    
    // Start monitoring the new token
    tokenManager.startMonitoring(token);
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): boolean {
    return this.token !== null && !tokenManager.isTokenExpired(this.token);
  }

  isTokenExpired(): boolean {
    return this.token ? tokenManager.isTokenExpired(this.token) : true;
  }
}

export const authService = new AuthService();
