# Data Models - Developer Social Network

This document defines all the TypeScript types and interfaces for the Socialistic developer social network application, designed to map to the backend models and API responses.

## Core Types

### User

```typescript
interface User {
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
  is_following: boolean;
  created_at: string;
  last_login: string | null;
}

// Minimal user representation for nested objects
interface UserPreview {
  id: number;
  username: string;
  full_name: string;
  profile_image: string | null;
  is_following: boolean;
}
```

### Post

```typescript
interface Post {
  id: number;
  author: UserPreview;
  content: string;
  code_snippet: string | null;
  programming_language: ProgrammingLanguage | null;
  created_at: string;
  updated_at: string;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
}

// For post creation/editing
interface PostFormData {
  content: string;
  code_snippet?: string;
  programming_language_id?: number | null;
}
```

### Comment

```typescript
interface Comment {
  id: number;
  author: UserPreview;
  post_id: number;
  content: string;
  created_at: string;
  updated_at: string;
  likes_count: number;
  is_liked: boolean;
}

// For comment creation/editing
interface CommentFormData {
  content: string;
}
```

### Project

```typescript
interface Project {
  id: number;
  creator: UserPreview;
  title: string;
  description: string;
  repo_url: string | null;
  tech_stack: Skill[];
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
  collaborators_count: number;
  is_collaborator: boolean;
  collaborators: ProjectCollaborator[];
}

type ProjectStatus = 'active' | 'completed' | 'on_hold' | 'archived';

// For project creation/editing
interface ProjectFormData {
  title: string;
  description: string;
  repo_url?: string;
  tech_stack_ids: number[];
  status?: ProjectStatus;
}
```

### ProjectCollaborator

```typescript
interface ProjectCollaborator {
  id: number;
  user: UserPreview;
  role: CollaboratorRole;
  joined_at: string;
}

type CollaboratorRole = 'owner' | 'admin' | 'contributor' | 'viewer';
```

### CollaborationRequest

```typescript
interface CollaborationRequest {
  id: number;
  project: {
    id: number;
    title: string;
  };
  user: UserPreview;
  message: string | null;
  status: CollaborationRequestStatus;
  created_at: string;
  updated_at: string;
}

type CollaborationRequestStatus = 'pending' | 'approved' | 'rejected';

// For creating a collaboration request
interface CollaborationRequestFormData {
  project_id: number;
  message?: string;
}

// For responding to a collaboration request
interface CollaborationResponseData {
  request_id: number;
  status: 'approved' | 'rejected';
  role?: CollaboratorRole;
}
```

### Skill

```typescript
interface Skill {
  id: number;
  name: string;
  category: SkillCategory;
}

type SkillCategory = 'frontend' | 'backend' | 'mobile' | 'devops' | 'database' | 'design' | 'other';
```

### ProgrammingLanguage

```typescript
interface ProgrammingLanguage {
  id: number;
  name: string;
  icon: string | null;
}
```

### Follow

```typescript
interface Follow {
  id: number;
  follower: UserPreview;
  following: UserPreview;
  created_at: string;
}
```

### Notification

```typescript
interface Notification {
  id: number;
  recipient_id: number;
  sender: UserPreview | null;
  type: NotificationType;
  content: string;
  read: boolean;
  created_at: string;
  related_object_id?: number;
  related_object_type?: string;
}

type NotificationType = 
  | 'like_post' 
  | 'like_comment' 
  | 'comment_post' 
  | 'follow' 
  | 'project_invite' 
  | 'project_request' 
  | 'project_request_approved' 
  | 'mention';
```

### NotificationSettings

```typescript
interface NotificationSettings {
  email_likes: boolean;
  email_comments: boolean;
  email_follows: boolean;
  email_mentions: boolean;
  email_project_invites: boolean;
  email_project_requests: boolean;
  push_likes: boolean;
  push_comments: boolean;
  push_follows: boolean;
  push_mentions: boolean;
  push_project_invites: boolean;
  push_project_requests: boolean;
}
```

## API Request/Response Types

### Authentication

```typescript
// Login
interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

// Registration
interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  full_name: string;
}

interface RegisterResponse {
  user: User;
  access: string;
  refresh: string;
}

// Token Refresh
interface RefreshTokenRequest {
  refresh: string;
}

interface RefreshTokenResponse {
  access: string;
}
```

### Pagination

```typescript
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

### Search

```typescript
// Common search parameters
interface SearchParams {
  query: string;
  page?: number;
  page_size?: number;
}

// User search
interface UserSearchParams extends SearchParams {
  skills?: string[];
}

// Post search
interface PostSearchParams extends SearchParams {
  programming_language?: string;
  date_from?: string;
  date_to?: string;
}

// Project search
interface ProjectSearchParams extends SearchParams {
  tech_stack?: string[];
  status?: ProjectStatus;
}

// Search results
interface SearchResults {
  users: PaginatedResponse<User>;
  posts: PaginatedResponse<Post>;
  projects: PaginatedResponse<Project>;
}
```

### Feed

```typescript
interface FeedParams {
  page?: number;
  page_size?: number;
  filter?: 'latest' | 'trending' | 'following';
}

type FeedResponse = PaginatedResponse<Post>;
```

## UI State Types

### Auth State

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
}
```

### UI State

```typescript
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  toasts: Toast[];
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

interface Toast {
  id: string;
  title: string;
  description?: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}
```

### Form States

```typescript
interface FormState<T> {
  isSubmitting: boolean;
  isValid: boolean;
  isDirty: boolean;
  errors: Record<keyof T, string>;
}
```

## Component State Types

```typescript
// Post interaction states
interface PostInteractionState {
  isLiking: boolean;
  isCommenting: boolean;
  isDeleting: boolean;
  showComments: boolean;
}

// Project interaction states
interface ProjectInteractionState {
  isRequesting: boolean;
  isLeaving: boolean;
}

// Search state
interface SearchState {
  query: string;
  activeTab: 'all' | 'users' | 'posts' | 'projects';
  filters: {
    users: UserSearchParams;
    posts: PostSearchParams;
    projects: ProjectSearchParams;
  };
}

// Notification state
interface NotificationState {
  unreadCount: number;
  isOpen: boolean;
  notifications: Notification[];
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: number) => Promise<void>;
}
```

## WebSocket Payloads

```typescript
// Base WebSocket message
interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

// Notification message
interface NotificationMessage extends WebSocketMessage {
  type: 'notification';
  notification: Notification;
}

// Status update message
interface StatusUpdateMessage extends WebSocketMessage {
  type: 'status_update';
  user_id: number;
  status: 'online' | 'offline' | 'away';
}

// Chat message
interface ChatMessage extends WebSocketMessage {
  type: 'chat_message';
  sender_id: number;
  recipient_id: number;
  content: string;
  timestamp: string;
  message_id: string;
}
```

## Utility Types

```typescript
// Type for ID parameters
type ID = number | string;

// Type for API errors
interface ApiError {
  status: number;
  message: string;
  errors?: Record<string, string[]>;
}

// Type for conditional rendering
type Maybe<T> = T | null | undefined;

// Type for loading states
interface LoadingState {
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
}

// Type for select options
interface SelectOption<T = string> {
  label: string;
  value: T;
}
```

These TypeScript interfaces and types provide a comprehensive type system for the frontend application, ensuring type safety and better developer experience when working with the API data. The models are designed to closely match the backend models while incorporating frontend-specific properties and methods as needed. 