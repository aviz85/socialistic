import axios, { AxiosError, AxiosResponse } from 'axios';
import { ApiError, ApiResponse, AuthToken, LoginCredentials, Post, ProgrammingLanguage, RegisterData, User } from '../types';

// Create axios instance with base URL
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // If the error is unauthorized and we haven't tried to refresh the token yet
    if (error.response?.status === 401 && !originalRequest?.headers?.['X-Retry']) {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        try {
          const { data } = await axios.post<AuthToken>('/api/auth/token/refresh/', {
            refresh: refreshToken,
          });
          
          localStorage.setItem('token', data.access);
          
          // Retry the original request with the new token
          if (originalRequest) {
            originalRequest.headers = {
              ...originalRequest.headers,
              Authorization: `Bearer ${data.access}`,
              'X-Retry': 'true',
            };
            return axios(originalRequest);
          }
        } catch (refreshError) {
          // If refresh token is invalid, logout user
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<{ user: User; tokens: AuthToken }> => {
    try {
      const response = await api.post<{ user: User; access: string; refresh: string }>('/auth/login/', credentials);
      return {
        user: response.data.user,
        tokens: {
          access: response.data.access,
          refresh: response.data.refresh,
        },
      };
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  register: async (data: RegisterData): Promise<{ user: User; tokens: AuthToken }> => {
    try {
      const response = await api.post<{ user: User; access: string; refresh: string }>('/auth/register/', data);
      return {
        user: response.data.user,
        tokens: {
          access: response.data.access,
          refresh: response.data.refresh,
        },
      };
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  getCurrentUser: async (): Promise<User> => {
    try {
      const response = await api.get<User>('/users/me/');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  logout: async (): Promise<void> => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh: refreshToken });
      }
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    } catch (error) {
      // Always clear local storage even if the API call fails
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
};

// Posts API
export const postsAPI = {
  getPosts: async (page = 1): Promise<ApiResponse<Post>> => {
    try {
      const response = await api.get<ApiResponse<Post>>('/posts/', { params: { page } });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  createPost: async (data: { content: string; code_snippet?: string | null; programming_language_id?: number }): Promise<Post> => {
    try {
      const response = await api.post<Post>('/posts/', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  likePost: async (postId: number): Promise<void> => {
    try {
      await api.post(`/posts/${postId}/like/`);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  unlikePost: async (postId: number): Promise<void> => {
    try {
      await api.delete(`/posts/${postId}/like/`);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
};

// Programming Languages API
export const programmingLanguagesAPI = {
  getLanguages: async (): Promise<ProgrammingLanguage[]> => {
    try {
      const response = await api.get<ApiResponse<ProgrammingLanguage>>('/programming-languages/');
      return response.data.results;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
};

// Users API
export const usersAPI = {
  getUser: async (userId: number): Promise<User> => {
    try {
      const response = await api.get<User>(`/users/${userId}/`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  updateProfile: async (data: Partial<User>): Promise<User> => {
    try {
      const response = await api.patch<User>('/users/me/', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  followUser: async (userId: number): Promise<void> => {
    try {
      await api.post(`/users/${userId}/follow/`);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
  
  unfollowUser: async (userId: number): Promise<void> => {
    try {
      await api.delete(`/users/${userId}/follow/`);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data as ApiError;
      }
      throw { message: 'An unknown error occurred' };
    }
  },
}; 