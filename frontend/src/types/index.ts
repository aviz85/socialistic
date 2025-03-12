// User related types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  bio: string | null;
  profile_image: string | null;
  github_profile: string | null;
  stackoverflow_profile: string | null;
  skills: Skill[];
  followers_count: number;
  following_count: number;
  is_following?: boolean;
  created_at: string;
}

export interface Skill {
  id: number;
  name: string;
  category: string;
}

export interface ProgrammingLanguage {
  id: number;
  name: string;
  icon: string | null;
}

// Post related types
export interface Post {
  id: number;
  author: User;
  content: string;
  code_snippet: string | null;
  programming_language: ProgrammingLanguage | null;
  created_at: string;
  updated_at: string;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
}

export interface Comment {
  id: number;
  author: User;
  post: number;
  content: string;
  created_at: string;
  updated_at: string;
  likes_count: number;
  is_liked: boolean;
}

// Auth related types
export interface AuthToken {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

// API response types
export interface ApiResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: any;
} 