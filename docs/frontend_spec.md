# Frontend Specification - Developer Social Network

## Technology Stack
- **React 18+**: Core UI library
- **TypeScript**: For type safety and better developer experience
- **Shadcn UI**: Component library built on Radix UI for accessible components
- **Tailwind CSS**: For styling
- **React Query**: For server state management
- **Zustand**: For client state management
- **React Router**: For routing
- **Axios**: For API requests
- **React Hook Form**: For form handling and validation
- **Zod**: For schema validation
- **React-Markdown**: For rendering markdown content
- **Day.js**: For date/time formatting
- **Prism.js**: For code syntax highlighting
- **Vitest**: For unit testing
- **Cypress**: For E2E testing

## Project Structure

```
src/
├── assets/                # Static assets (icons, images)
├── components/            # Reusable components
│   ├── ui/                # Shadcn UI components
│   ├── auth/              # Authentication related components
│   ├── layout/            # Layout components
│   ├── posts/             # Post related components
│   ├── projects/          # Project related components
│   ├── profiles/          # User profile components
│   ├── notifications/     # Notification components
│   └── common/            # Common utility components
├── context/               # React context providers
├── features/              # Feature-specific components grouped by domain
│   ├── auth/
│   ├── feed/
│   ├── messaging/
│   ├── notifications/
│   ├── posts/
│   ├── profiles/
│   └── projects/
├── hooks/                 # Custom React hooks
├── lib/                   # Utility functions and shared code
│   ├── api/               # API client and service functions
│   ├── utils/             # Utility functions
│   ├── validation/        # Schema validations
│   └── constants.ts       # Application constants
├── pages/                 # Page components for routing
├── store/                 # Zustand stores
├── styles/                # Global styles
├── types/                 # TypeScript type definitions
├── App.tsx                # Main App component
├── main.tsx               # Entry point
└── vite-env.d.ts          # Vite type declarations
```

## Component Architecture

### Core Component Categories

#### Layout Components
- `Shell`: Main application shell with navigation
- `Header`: App header with logo, search, and actions
- `Sidebar`: Navigation sidebar
- `Footer`: App footer
- `PageLayout`: Standard page layout wrapper

#### Auth Components
- `LoginForm`: User login form
- `RegisterForm`: User registration form
- `AuthProvider`: Authentication context provider
- `ProtectedRoute`: Route wrapper for authenticated routes

#### User Components
- `UserProfile`: User profile display
- `ProfileEditor`: Edit profile form
- `UserCard`: Compact user display card
- `FollowButton`: Button to follow/unfollow users
- `SkillBadge`: Display user skills as badges

#### Post Components
- `PostCard`: Display a post with interactions
- `PostForm`: Create/edit post form
- `CodeSnippet`: Code display with syntax highlighting
- `PostComments`: Comments section for a post
- `PostActions`: Like, comment, share actions

#### Project Components
- `ProjectCard`: Display project summary
- `ProjectForm`: Create/edit project form
- `ProjectDetails`: Full project view
- `CollaborationRequest`: Request to join component

#### Notification Components
- `NotificationCenter`: Notifications dropdown
- `NotificationItem`: Individual notification display
- `NotificationBadge`: Unread count indicator

#### Search Components
- `SearchBar`: Global search input
- `SearchFilters`: Filter search results
- `SearchResults`: Display categorized search results

## Routing Structure

```
/                           # Home/Feed
/login                      # Login page
/register                   # Registration page
/profile                    # Current user profile
/profile/edit               # Edit profile
/user/:username             # User profile by username
/posts                      # All posts
/posts/:id                  # Single post with comments
/posts/create               # Create post
/projects                   # Browse projects
/projects/:id               # Single project view
/projects/create            # Create project
/notifications              # All notifications
/search                     # Search results
/settings                   # User settings
/messaging                  # Private messaging
/trending                   # Trending content
```

## State Management

### Authentication State (Zustand)
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
}
```

### UI State (Zustand)
```typescript
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}
```

### Notifications State (React Query + WebSocket)
```typescript
// Using React Query for initial data and WebSocket for real-time updates
const useNotifications = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['notifications'],
    queryFn: fetchNotifications
  });
  
  // WebSocket connection for real-time updates
  useEffect(() => {
    // Setup WebSocket connection
    // Handle incoming notifications
    return () => {
      // Clean up WebSocket connection
    };
  }, []);
  
  return { notifications: data, isLoading, error };
};
```

## API Integration

### API Client with Axios
```typescript
// src/lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Call token refresh logic
        const refreshToken = localStorage.getItem('refreshToken');
        const { data } = await axios.post('/api/auth/token/refresh/', {
          refresh: refreshToken,
        });
        localStorage.setItem('token', data.access);
        apiClient.defaults.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Handle refresh token failure (logout)
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### API Services Structure
```typescript
// src/lib/api/services/auth.ts
import apiClient from '../client';
import { User, LoginCredentials, RegisterData } from '@/types';

export const authService = {
  login: async (credentials: LoginCredentials) => {
    const { data } = await apiClient.post('/api/auth/login/', credentials);
    return data;
  },
  
  register: async (userData: RegisterData) => {
    const { data } = await apiClient.post('/api/auth/register/', userData);
    return data;
  },
  
  getCurrentUser: async () => {
    const { data } = await apiClient.get<User>('/api/auth/me/');
    return data;
  },
  
  logout: async () => {
    return await apiClient.post('/api/auth/logout/');
  },
};

// Similar services for posts, projects, users, etc.
```

## Authentication Flow

1. **User Registration**:
   - Form validation with React Hook Form + Zod
   - Submit to `/api/auth/register/`
   - Store tokens in localStorage
   - Redirect to profile completion or home

2. **User Login**:
   - Form validation with React Hook Form + Zod
   - Submit to `/api/auth/login/`
   - Store tokens in localStorage
   - Redirect to previous page or home

3. **Token Refresh**:
   - Automatic refresh using axios interceptors
   - Handle refresh token expiration

4. **Logout**:
   - Clear tokens from localStorage
   - Call `/api/auth/logout/`
   - Redirect to login page

## UI Design System

### Theme
- **Color Palette**:
  - Primary: indigo-600 (#4F46E5)
  - Secondary: emerald-500 (#10B981)
  - Accent: amber-500 (#F59E0B)
  - Neutral: slate-800 (#1E293B)
  - Background: slate-50 (#F8FAFC)
  - Dark mode: slate-900 (#0F172A)

- **Typography**:
  - Font family: Inter
  - Headings: Weights 700 (bold), 600 (semibold)
  - Body: Weights 400 (regular), 500 (medium)
  - Code: Fira Code, monospace

- **Spacing**:
  - Using Tailwind's default spacing scale (4, 8, 12, 16, 20...)
  - Consistent component spacing with 4px grid

- **Shadows**:
  - Using Tailwind's shadow utilities
  - Custom shadows for cards and modals

- **Border Radius**:
  - Buttons, cards: rounded-md (0.375rem)
  - Pills, badges: rounded-full

### Core Components (Shadcn UI)
- `Button`: Primary, secondary, ghost, outline, and danger variants
- `Input`: Text inputs with validation states
- `Card`: For posts, projects, and user profiles
- `Dialog`: For modals and confirmation dialogs
- `Dropdown Menu`: For actions and options
- `Tabs`: For switching between content views
- `Toast`: For notifications and alerts
- `Avatar`: For user profile pictures
- `Badge`: For skills, tags, and status indicators
- `Skeleton`: For loading states

## Page Implementations

### Home/Feed Page
- **Features**:
  - Feed of posts from followed users
  - Create post input
  - Trending topics sidebar
  - Suggested users to follow
- **Components**:
  - `FeedLayout`
  - `PostList`
  - `PostComposer`
  - `TrendingSidebar`
  - `SuggestedUsers`
- **State**:
  - Posts from API with pagination
  - Post creation form state
  - Feed filters (latest, trending)

### User Profile Page
- **Features**:
  - Profile header with user details
  - Tabs for posts, projects, and activity
  - Follow/unfollow functionality
  - Skills and experience list
- **Components**:
  - `ProfileHeader`
  - `ProfileTabs`
  - `UserPostsList`
  - `UserProjectsList`
  - `SkillsList`
- **State**:
  - User profile data
  - Follow status
  - Active tab

### Post Detail Page
- **Features**:
  - Full post content with code highlighting
  - Comments thread
  - Like/unlike functionality
  - Share options
- **Components**:
  - `PostDetailCard`
  - `CodeBlock`
  - `CommentsList`
  - `CommentForm`
  - `PostActions`
- **State**:
  - Post data
  - Comments with pagination
  - Like status
  - Comment form state

### Projects Page
- **Features**:
  - Project listings with filters
  - Create project button
  - Tech stack filtering
  - Status indicators (active, completed, seeking)
- **Components**:
  - `ProjectsGrid`
  - `ProjectFilters`
  - `ProjectCard`
  - `TechStackTags`
- **State**:
  - Projects list with filters
  - Filter state

## Real-time Features Implementation

### WebSocket Integration
```typescript
// src/lib/socket.ts
import { useAuthStore } from '@/store/authStore';

export const createWebSocketConnection = () => {
  const token = useAuthStore.getState().token;
  const socket = new WebSocket(`${import.meta.env.VITE_WS_URL}?token=${token}`);
  
  socket.onopen = () => {
    console.log('WebSocket connection established');
  };
  
  socket.onclose = () => {
    console.log('WebSocket connection closed');
    // Reconnection logic
  };
  
  return socket;
};

export const useWebSocket = (onMessage: (data: any) => void) => {
  useEffect(() => {
    const socket = createWebSocketConnection();
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    return () => {
      socket.close();
    };
  }, [onMessage]);
};
```

### Real-time Notifications
```typescript
// src/features/notifications/NotificationsProvider.tsx
import { useWebSocket } from '@/lib/socket';
import { useNotificationStore } from '@/store/notificationStore';

export const NotificationsProvider = ({ children }) => {
  const { addNotification } = useNotificationStore();
  
  useWebSocket((data) => {
    if (data.type === 'notification') {
      addNotification(data.notification);
      // Show toast notification
      toast({
        title: data.notification.title,
        description: data.notification.message,
      });
    }
  });
  
  return <>{children}</>;
};
```

## Accessibility Considerations

- Using Shadcn UI components which are built on Radix UI for accessible foundations
- Semantic HTML structure
- ARIA attributes where needed
- Keyboard navigation support
- Focus management for modals and dialogs
- Color contrast compliance
- Screen reader friendly content
- Motion reduction for animations

## Performance Optimization

- Code splitting with React.lazy() and Suspense
- Image optimization with responsive images
- Memoization of expensive components with useMemo and React.memo
- Virtualized lists for long content (react-window)
- Prefetching data for common navigation paths
- Optimistic UI updates for better user experience

## Development Workflow

1. **Setup**:
   - Initialize project with Vite
   - Install dependencies
   - Configure Shadcn UI
   - Set up ESLint and Prettier
   - Configure TypeScript

2. **Component Development**:
   - Build base UI components
   - Create layout components
   - Implement authentication flows
   - Develop feature components

3. **API Integration**:
   - Set up API client
   - Implement service functions
   - Connect components to API
   - Handle loading and error states

4. **Testing**:
   - Unit tests for utilities and hooks
   - Component tests with Vitest
   - E2E tests with Cypress

5. **Deployment**:
   - Build optimization
   - Environment configuration
   - CI/CD setup

## Implementation Priorities

1. **Core Infrastructure** (Week 1-2)
   - Project setup and configuration
   - Authentication system
   - Base layout and navigation
   - API client and interceptors

2. **Essential Features** (Week 3-4)
   - User profiles
   - Feed implementation
   - Post creation and viewing
   - Comments and likes

3. **Social Features** (Week 5-6)
   - Follow/unfollow functionality
   - Notifications system
   - Real-time updates
   - Search functionality

4. **Project Collaboration** (Week 7-8)
   - Project listing and creation
   - Collaboration requests
   - Project management

5. **Advanced Features** (Week 9-10)
   - Messaging system
   - Advanced code sharing
   - Analytics dashboards
   - Performance optimization

## Key Metrics & Analytics

- Page load time and performance metrics
- User engagement (time on site, actions per session)
- Feature usage statistics
- Error tracking and monitoring
- User feedback collection

## Mobile Responsiveness

- Mobile-first design approach
- Responsive layouts using Tailwind breakpoints
- Touch-friendly UI elements
- Optimized navigation for small screens
- Adaptive content presentation 