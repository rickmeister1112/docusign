// TypeScript interfaces for feedback data
export interface Feedback {
  id: number;
  text: string;
  upvotes: number;
  user_id: number;
  user_email: string;
  created_at: string;
  updated_at?: string;
  has_upvoted: boolean;
}

export interface FeedbackCreate {
  text: string;
}

export interface FeedbackUpdate {
  text?: string;
}

export interface UpvoteResponse {
  id: number;
  upvotes: number;
  has_upvoted: boolean;
  message: string;
}

// Authentication types
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}
