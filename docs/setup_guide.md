# Frontend Setup Guide - Developer Social Network

This guide provides step-by-step instructions for setting up the developer social network frontend project, configuring dependencies, and establishing a development workflow.

## Prerequisites

- Node.js (v18.0.0 or higher)
- npm (v8.0.0 or higher) or yarn (v1.22.0 or higher)
- Git

## Project Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/socialistic.git
cd socialistic/frontend
```

### 2. Install Dependencies

```bash
# Using npm
npm install

# Using yarn
yarn install
```

### 3. Set Up Environment Variables

Create a `.env.local` file in the root of the frontend directory:

```
# API Configuration
VITE_API_BASE_URL=http://localhost:8050/api
VITE_WS_URL=ws://localhost:8050/ws

# Authentication
VITE_AUTH_STORAGE_KEY=socialistic_auth
VITE_AUTH_TOKEN_EXPIRY=3600

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_MESSAGING=true
```

## Installing Shadcn UI

We use Shadcn UI as our component library, which requires some additional setup.

### 1. Initialize Shadcn UI

```bash
npx shadcn-ui@latest init
```

When prompted, select:
- Typography: Yes
- Style: Default (or your preference)
- Base color: Slate (or your preference)
- Global CSS: src/styles/globals.css
- CSS variables: Yes
- React Server Components: No
- Path alias: @/*

### 2. Install Core Components

```bash
# Install essential UI components
npx shadcn-ui@latest add button card input form select textarea toast avatar badge dialog dropdown-menu tabs
```

## Project Structure Setup

Create the following directory structure:

```bash
mkdir -p src/{components,features,lib,pages,store,hooks,context,assets,styles,types}
mkdir -p src/components/{ui,auth,layout,posts,projects,profiles,notifications,common}
mkdir -p src/features/{auth,feed,messaging,notifications,posts,profiles,projects}
mkdir -p src/lib/{api,utils,validation}
```

## TypeScript Configuration

Create or update the `tsconfig.json` file:

```bash
# Create TypeScript configuration
cat > tsconfig.json << EOL
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOL
```

## Setting Up API Client

Create a basic API client:

```bash
# Create API client file
mkdir -p src/lib/api
cat > src/lib/api/client.ts << EOL
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
apiClient.interceptors.request.use(config => {
  const authData = localStorage.getItem(import.meta.env.VITE_AUTH_STORAGE_KEY);
  if (authData) {
    const { token } = JSON.parse(authData);
    if (token) {
      config.headers.Authorization = \`Bearer \${token}\`;
    }
  }
  return config;
});

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Handle 401 responses for expired tokens
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const authData = localStorage.getItem(import.meta.env.VITE_AUTH_STORAGE_KEY);
        if (authData) {
          const { refreshToken } = JSON.parse(authData);
          
          const { data } = await axios.post(
            \`\${import.meta.env.VITE_API_BASE_URL}/auth/token/refresh/\`,
            { refresh: refreshToken }
          );
          
          // Update stored token
          const currentAuthData = JSON.parse(
            localStorage.getItem(import.meta.env.VITE_AUTH_STORAGE_KEY) || '{}'
          );
          
          localStorage.setItem(
            import.meta.env.VITE_AUTH_STORAGE_KEY,
            JSON.stringify({
              ...currentAuthData,
              token: data.access,
            })
          );
          
          // Retry with new token
          originalRequest.headers.Authorization = \`Bearer \${data.access}\`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Handle refresh token failure
        localStorage.removeItem(import.meta.env.VITE_AUTH_STORAGE_KEY);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
EOL
```

## Setting Up Authentication Store

Create a basic authentication store with Zustand:

```bash
# Create auth store
mkdir -p src/store
cat > src/store/authStore.ts << EOL
import { create } from 'zustand';
import apiClient from '@/lib/api/client';
import { User, LoginCredentials, RegisterData } from '@/types';

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
  refreshAuthToken: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => {
  // Initialize from localStorage if available
  const storedData = localStorage.getItem(import.meta.env.VITE_AUTH_STORAGE_KEY);
  const initialData = storedData ? JSON.parse(storedData) : { user: null, token: null, refreshToken: null };
  
  return {
    user: initialData.user,
    token: initialData.token,
    refreshToken: initialData.refreshToken,
    isAuthenticated: !!initialData.token,
    isLoading: false,
    error: null,
    
    login: async (credentials) => {
      set({ isLoading: true, error: null });
      
      try {
        const { data } = await apiClient.post('/auth/login/', credentials);
        
        // Store in state
        set({
          user: data.user,
          token: data.access,
          refreshToken: data.refresh,
          isAuthenticated: true,
          isLoading: false
        });
        
        // Store in localStorage
        localStorage.setItem(
          import.meta.env.VITE_AUTH_STORAGE_KEY,
          JSON.stringify({
            user: data.user,
            token: data.access,
            refreshToken: data.refresh
          })
        );
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.message || 'Login failed'
        });
        throw error;
      }
    },
    
    register: async (userData) => {
      set({ isLoading: true, error: null });
      
      try {
        const { data } = await apiClient.post('/auth/register/', userData);
        
        // Store in state
        set({
          user: data.user,
          token: data.access,
          refreshToken: data.refresh,
          isAuthenticated: true,
          isLoading: false
        });
        
        // Store in localStorage
        localStorage.setItem(
          import.meta.env.VITE_AUTH_STORAGE_KEY,
          JSON.stringify({
            user: data.user,
            token: data.access,
            refreshToken: data.refresh
          })
        );
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.message || 'Registration failed'
        });
        throw error;
      }
    },
    
    logout: () => {
      // Clear server-side session
      apiClient.post('/auth/logout/').catch(() => {
        // Ignore errors during logout
      });
      
      // Clear client-side state
      localStorage.removeItem(import.meta.env.VITE_AUTH_STORAGE_KEY);
      set({
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false
      });
    },
    
    refreshAuthToken: async () => {
      const { refreshToken } = get();
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      try {
        const { data } = await apiClient.post('/auth/token/refresh/', {
          refresh: refreshToken
        });
        
        // Update token in state
        set({ token: data.access });
        
        // Update token in localStorage
        const storedData = localStorage.getItem(import.meta.env.VITE_AUTH_STORAGE_KEY);
        if (storedData) {
          const parsedData = JSON.parse(storedData);
          localStorage.setItem(
            import.meta.env.VITE_AUTH_STORAGE_KEY,
            JSON.stringify({
              ...parsedData,
              token: data.access
            })
          );
        }
      } catch (error) {
        // Handle refresh failure
        get().logout();
        throw error;
      }
    },
    
    updateUser: async (userData) => {
      set({ isLoading: true, error: null });
      
      try {
        const { data } = await apiClient.put('/auth/me/', userData);
        
        // Update user in state
        set({
          user: data,
          isLoading: false
        });
        
        // Update user in localStorage
        const storedData = localStorage.getItem(import.meta.env.VITE_AUTH_STORAGE_KEY);
        if (storedData) {
          const parsedData = JSON.parse(storedData);
          localStorage.setItem(
            import.meta.env.VITE_AUTH_STORAGE_KEY,
            JSON.stringify({
              ...parsedData,
              user: data
            })
          );
        }
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.message || 'Failed to update profile'
        });
        throw error;
      }
    }
  };
});
EOL
```

## Create Base Layout Components

Set up the basic layout components:

```bash
# Create Shell component
mkdir -p src/components/layout
cat > src/components/layout/Shell.tsx << EOL
import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { useUIStore } from '@/store/uiStore';

interface ShellProps {
  children: React.ReactNode;
}

export function Shell({ children }: ShellProps) {
  const { sidebarOpen } = useUIStore();
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex">
        <Sidebar />
        <main className={\`flex-1 p-4 md:p-6 transition-all \${
          sidebarOpen ? 'md:ml-64' : 'ml-0'
        }\`}>
          <div className="container mx-auto">{children}</div>
        </main>
      </div>
      <Footer />
    </div>
  );
}

export default Shell;
EOL

# Create placeholder components for Header, Sidebar, Footer
cat > src/components/layout/Header.tsx << EOL
import React from 'react';
import { useUIStore } from '@/store/uiStore';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

const Header = () => {
  const { toggleSidebar } = useUIStore();
  const { isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  
  return (
    <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30">
      <div className="container mx-auto flex items-center justify-between h-16 px-4">
        <div className="flex items-center">
          <Button 
            variant="ghost" 
            className="mr-2 md:hidden" 
            onClick={toggleSidebar}
            size="icon"
          >
            <span className="sr-only">Toggle menu</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-6 w-6"
            >
              <line x1="3" x2="21" y1="6" y2="6" />
              <line x1="3" x2="21" y1="12" y2="12" />
              <line x1="3" x2="21" y1="18" y2="18" />
            </svg>
          </Button>
          <div 
            className="font-bold text-xl cursor-pointer"
            onClick={() => navigate('/')}
          >
            Socialistic
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            <Button variant="ghost" onClick={() => logout()}>
              Logout
            </Button>
          ) : (
            <Button onClick={() => navigate('/login')}>
              Login
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
EOL

cat > src/components/layout/Sidebar.tsx << EOL
import React from 'react';
import { useUIStore } from '@/store/uiStore';

const Sidebar = () => {
  const { sidebarOpen } = useUIStore();
  
  if (!sidebarOpen) return null;
  
  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 z-20 transform transition-transform duration-200 ease-in-out md:translate-x-0 pt-16">
      <nav className="px-4 py-6">
        <ul className="space-y-2">
          <li>
            <a 
              href="/" 
              className="flex items-center px-4 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md"
            >
              <span>Home</span>
            </a>
          </li>
          <li>
            <a 
              href="/projects" 
              className="flex items-center px-4 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md"
            >
              <span>Projects</span>
            </a>
          </li>
          <li>
            <a 
              href="/profile" 
              className="flex items-center px-4 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md"
            >
              <span>Profile</span>
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
EOL

cat > src/components/layout/Footer.tsx << EOL
import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-slate-500 dark:text-slate-400">
              © {new Date().getFullYear()} Socialistic. All rights reserved.
            </p>
          </div>
          <div className="flex space-x-6">
            <a href="#" className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Terms
            </a>
            <a href="#" className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Privacy
            </a>
            <a href="#" className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
EOL
```

## Setting Up React Router

Create the app routing structure:

```bash
# Create router configuration
mkdir -p src/pages
cat > src/App.tsx << EOL
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import Shell from '@/components/layout/Shell';
import HomePage from '@/pages/HomePage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import ProfilePage from '@/pages/ProfilePage';
import ProjectsPage from '@/pages/ProjectsPage';
import NotFoundPage from '@/pages/NotFoundPage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Shell>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              } 
            />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Shell>
      </Router>
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;
EOL
```

## Create Placeholder Pages

```bash
# Create placeholder pages
cat > src/pages/HomePage.tsx << EOL
import React from 'react';

const HomePage = () => {
  return (
    <div className="space-y-6">
      <div className="text-2xl font-bold">Home Page</div>
      <p>Welcome to Socialistic, a social network for developers.</p>
    </div>
  );
};

export default HomePage;
EOL

cat > src/pages/LoginPage.tsx << EOL
import React from 'react';

const LoginPage = () => {
  return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="text-2xl font-bold">Login</div>
      <p>Login form will go here.</p>
    </div>
  );
};

export default LoginPage;
EOL

cat > src/pages/RegisterPage.tsx << EOL
import React from 'react';

const RegisterPage = () => {
  return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="text-2xl font-bold">Register</div>
      <p>Registration form will go here.</p>
    </div>
  );
};

export default RegisterPage;
EOL

cat > src/pages/ProfilePage.tsx << EOL
import React from 'react';

const ProfilePage = () => {
  return (
    <div className="space-y-6">
      <div className="text-2xl font-bold">Profile</div>
      <p>User profile will go here.</p>
    </div>
  );
};

export default ProfilePage;
EOL

cat > src/pages/ProjectsPage.tsx << EOL
import React from 'react';

const ProjectsPage = () => {
  return (
    <div className="space-y-6">
      <div className="text-2xl font-bold">Projects</div>
      <p>Projects list will go here.</p>
    </div>
  );
};

export default ProjectsPage;
EOL

cat > src/pages/NotFoundPage.tsx << EOL
import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] space-y-6">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-xl">Page not found</p>
      <Link to="/" className="text-blue-500 hover:underline">
        Return home
      </Link>
    </div>
  );
};

export default NotFoundPage;
EOL
```

## Create Protected Route Component

```bash
# Create protected route component
mkdir -p src/components/auth
cat > src/components/auth/ProtectedRoute.tsx << EOL
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

const ProtectedRoute = ({ 
  children, 
  redirectTo = '/login' 
}: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  const location = useLocation();
  
  if (isLoading) {
    // Show loading spinner when checking authentication
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    // Redirect to login with the current location as a "from" parameter
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }
  
  return <>{children}</>;
};

export default ProtectedRoute;
EOL
```

## Scripts and Development Workflow

Update the `package.json` scripts:

```bash
# Update package.json scripts
npm pkg set scripts.dev="vite"
npm pkg set scripts.build="tsc && vite build"
npm pkg set scripts.lint="eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
npm pkg set scripts.preview="vite preview"
npm pkg set scripts.format="prettier --write \"src/**/*.{ts,tsx}\""
npm pkg set scripts.test="vitest run"
npm pkg set scripts.test:watch="vitest"
npm pkg set scripts.test:coverage="vitest run --coverage"
```

## Development Workflow

The typical development workflow consists of:

1. **Starting the Development Server**:
   ```bash
   npm run dev
   ```

2. **Creating New Components**:
   - Create component files in the appropriate directory.
   - Use Shadcn UI components as building blocks for your custom components.
   - Follow TypeScript typing for better development experience.

3. **Testing**:
   ```bash
   npm run test:watch
   ```

4. **Building for Production**:
   ```bash
   npm run build
   ```

5. **Code Formatting**:
   ```bash
   npm run format
   ```

## Code Style and Best Practices

- **Component Organization**: Group components by feature or domain.
- **State Management**: Use Zustand for global state, React Query for server state.
- **Typing**: Always define TypeScript interfaces for props and state.
- **Error Handling**: Implement proper error handling with error boundaries.
- **Accessibility**: Follow accessibility best practices using Shadcn UI's built-in accessibility features.
- **Performance**: Utilize memoization and code-splitting where appropriate.

## Recommended Extensions (VS Code)

- ESLint
- Prettier
- Tailwind CSS IntelliSense
- ES7+ React/Redux/React-Native snippets
- JavaScript and TypeScript Nightly
- vscode-styled-components

## Common Issues and Solutions

### API CORS Issues

If you encounter CORS issues when connecting to the API:

1. Ensure the backend server is configured to allow requests from your frontend domain.
2. Verify environment variables are correctly set.
3. Check if authentication headers are properly being sent.

### Authentication Problems

If you experience authentication issues:

1. Check the console for token-related errors.
2. Verify that the token is being stored correctly in localStorage.
3. Ensure the token refresh mechanism is working.

### Styling Issues

For Tailwind and Shadcn UI styling problems:

1. Verify the Tailwind configuration is correct.
2. Check for classname conflicts.
3. Use the browser inspector to debug style inheritance problems.

## Deployment

For production deployment:

1. Build the project:
   ```bash
   npm run build
   ```

2. Test the production build locally:
   ```bash
   npm run preview
   ```

3. Deploy the `dist` directory to your hosting provider or CI/CD pipeline.

## Additional Resources

- [React Documentation](https://reactjs.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Shadcn UI Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Zustand Documentation](https://github.com/pmndrs/zustand) 