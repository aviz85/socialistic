# Component Architecture - Developer Social Network

This document provides a detailed breakdown of all the core components in the Socialistic developer social network application, including their props, state, and relationships.

## Layout Components

### Shell

The main application wrapper that contains the overall layout structure.

```tsx
// Props
interface ShellProps {
  children: React.ReactNode;
}

// Usage
<Shell>
  <Header />
  <Sidebar />
  <main>{children}</main>
  <Footer />
</Shell>
```

### Header

The top navigation bar containing the logo, search, navigation links, and user menu.

```tsx
// Props
interface HeaderProps {
  onSearch?: (query: string) => void;
}

// State
const [isSearchOpen, setIsSearchOpen] = useState(false);
const [notifications, notificationCount] = useNotifications();

// Usage
<Header onSearch={handleSearch} />
```

### Sidebar

The main navigation sidebar with links to different sections of the app.

```tsx
// Props
interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

// Usage
<Sidebar isOpen={sidebarOpen} onClose={toggleSidebar} />
```

### PageLayout

A reusable layout component for standard pages with customizable elements.

```tsx
// Props
interface PageLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
  backLink?: string;
  backLinkText?: string;
  actions?: React.ReactNode;
  sidebar?: React.ReactNode;
}

// Usage
<PageLayout 
  title="Projects"
  description="Discover collaboration opportunities"
  actions={<Button>Create Project</Button>}
>
  {children}
</PageLayout>
```

## Auth Components

### LoginForm

Form for user authentication.

```tsx
// Props
interface LoginFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

// Form State (React Hook Form)
const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
  resolver: zodResolver(loginSchema)
});

// Usage
<LoginForm onSuccess={() => navigate('/feed')} />
```

### RegisterForm

Form for new user registration.

```tsx
// Props
interface RegisterFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

// Form State (React Hook Form)
const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
  resolver: zodResolver(registerSchema)
});

// Usage
<RegisterForm onSuccess={() => navigate('/profile/edit')} />
```

### AuthProvider

Context provider for authentication state.

```tsx
// Context
export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
}

// Usage
<AuthProvider>
  <App />
</AuthProvider>
```

### ProtectedRoute

Component that restricts access to authenticated users.

```tsx
// Props
interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

// Usage
<ProtectedRoute redirectTo="/login">
  <ProfilePage />
</ProtectedRoute>
```

## User Components

### UserProfile

Displays a user's profile information.

```tsx
// Props
interface UserProfileProps {
  userId: string | number;
  isCurrentUser?: boolean;
}

// State (React Query)
const { data: user, isLoading, error } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => userService.getUserById(userId)
});

// Usage
<UserProfile userId={123} isCurrentUser={false} />
```

### ProfileEditor

Form for editing user profile information.

```tsx
// Props
interface ProfileEditorProps {
  user: User;
  onSave?: (updatedUser: User) => void;
}

// Form State (React Hook Form)
const { register, handleSubmit, formState: { errors } } = useForm<ProfileFormData>({
  resolver: zodResolver(profileSchema),
  defaultValues: {
    username: user.username,
    fullName: user.full_name,
    bio: user.bio,
    // ...other fields
  }
});

// Usage
<ProfileEditor user={currentUser} onSave={handleProfileUpdate} />
```

### UserCard

Compact user card for displaying in lists, search results, etc.

```tsx
// Props
interface UserCardProps {
  user: User;
  action?: React.ReactNode;
  isFollowing?: boolean;
  onFollow?: () => void;
  onUnfollow?: () => void;
}

// Usage
<UserCard 
  user={user}
  isFollowing={true}
  onFollow={handleFollow} 
  onUnfollow={handleUnfollow}
/>
```

### FollowButton

Button for following/unfollowing a user.

```tsx
// Props
interface FollowButtonProps {
  userId: string | number;
  isFollowing: boolean;
  onSuccess?: () => void;
}

// State (React Query)
const followMutation = useMutation({
  mutationFn: () => userService.followUser(userId),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['user', userId] });
    onSuccess?.();
  }
});

const unfollowMutation = useMutation({
  mutationFn: () => userService.unfollowUser(userId),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['user', userId] });
    onSuccess?.();
  }
});

// Usage
<FollowButton 
  userId={123}
  isFollowing={true}
  onSuccess={() => refreshUserData()}
/>
```

### SkillBadge

Displays a user skill as a badge.

```tsx
// Props
interface SkillBadgeProps {
  skill: Skill;
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

// Usage
<SkillBadge 
  skill={{ id: 1, name: 'React', category: 'frontend' }}
  size="md"
  onClick={() => navigateToSkillSearch(skill.name)}
/>
```

## Post Components

### PostCard

Card displaying a post with interactions.

```tsx
// Props
interface PostCardProps {
  post: Post;
  isDetailed?: boolean;
  onLike?: () => void;
  onComment?: () => void;
  onShare?: () => void;
}

// State (React Query)
const likeMutation = useMutation({
  mutationFn: () => postService.likePost(post.id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['post', post.id] });
  }
});

// Usage
<PostCard 
  post={post}
  isDetailed={false}
  onLike={handleLike}
  onComment={() => navigate(`/posts/${post.id}`)}
  onShare={handleShare}
/>
```

### PostForm

Form for creating or editing a post.

```tsx
// Props
interface PostFormProps {
  initialValues?: Partial<PostFormData>;
  onSubmit: (data: PostFormData) => void;
  isEdit?: boolean;
}

// Form State (React Hook Form)
const { register, handleSubmit, formState: { errors } } = useForm<PostFormData>({
  resolver: zodResolver(postSchema),
  defaultValues: initialValues
});

// State
const [selectedLanguage, setSelectedLanguage] = useState<string | null>(
  initialValues?.programming_language || null
);

// Usage
<PostForm 
  initialValues={{ content: "Draft post" }}
  onSubmit={handleCreatePost}
  isEdit={false}
/>
```

### CodeSnippet

Displays code with syntax highlighting.

```tsx
// Props
interface CodeSnippetProps {
  code: string;
  language: string;
  showLineNumbers?: boolean;
  wrapLines?: boolean;
}

// Usage
<CodeSnippet 
  code="console.log('Hello World');"
  language="javascript"
  showLineNumbers={true}
  wrapLines={false}
/>
```

### PostComments

Display and manage comments for a post.

```tsx
// Props
interface PostCommentsProps {
  postId: string | number;
  initialComments?: Comment[];
}

// State (React Query)
const { data: comments, isLoading, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['comments', postId],
  queryFn: ({ pageParam = 1 }) => commentService.getComments(postId, pageParam),
  getNextPageParam: (lastPage) => lastPage.nextPage
});

// Usage
<PostComments 
  postId={123}
  initialComments={initialCommentsData}
/>
```

### PostActions

Action buttons for post interactions.

```tsx
// Props
interface PostActionsProps {
  postId: string | number;
  isLiked: boolean;
  likesCount: number;
  commentsCount: number;
  onLikeToggle: () => void;
  onCommentClick: () => void;
  onShareClick: () => void;
}

// Usage
<PostActions 
  postId={123}
  isLiked={true}
  likesCount={42}
  commentsCount={7}
  onLikeToggle={handleLikeToggle}
  onCommentClick={() => setShowComments(true)}
  onShareClick={handleShare}
/>
```

## Project Components

### ProjectCard

Card displaying project summary information.

```tsx
// Props
interface ProjectCardProps {
  project: Project;
  isCollaborator?: boolean;
  onViewDetails?: () => void;
}

// Usage
<ProjectCard 
  project={project}
  isCollaborator={true}
  onViewDetails={() => navigate(`/projects/${project.id}`)}
/>
```

### ProjectForm

Form for creating or editing a project.

```tsx
// Props
interface ProjectFormProps {
  initialValues?: Partial<ProjectFormData>;
  onSubmit: (data: ProjectFormData) => void;
  isEdit?: boolean;
}

// Form State (React Hook Form)
const { register, handleSubmit, control, formState: { errors } } = useForm<ProjectFormData>({
  resolver: zodResolver(projectSchema),
  defaultValues: initialValues
});

// State
const [selectedTechStack, setSelectedTechStack] = useState<Skill[]>(
  initialValues?.tech_stack || []
);

// Usage
<ProjectForm 
  initialValues={{ title: "My Project" }}
  onSubmit={handleCreateProject}
  isEdit={false}
/>
```

### ProjectDetails

Detailed view of a project with collaborators and actions.

```tsx
// Props
interface ProjectDetailsProps {
  projectId: string | number;
  isOwner?: boolean;
}

// State (React Query)
const { data: project, isLoading, error } = useQuery({
  queryKey: ['project', projectId],
  queryFn: () => projectService.getProjectById(projectId)
});

// Usage
<ProjectDetails
  projectId={123}
  isOwner={true}
/>
```

### CollaborationRequest

Component for requesting to join a project or managing requests.

```tsx
// Props
interface CollaborationRequestProps {
  projectId: string | number;
  isOwner?: boolean;
}

// State (React Query)
const { data: requests, isLoading } = useQuery({
  queryKey: ['collaboration-requests', projectId],
  queryFn: () => projectService.getCollaborationRequests(projectId),
  enabled: isOwner
});

const requestMutation = useMutation({
  mutationFn: () => projectService.requestCollaboration(projectId),
  onSuccess: () => {
    // Show success notification
  }
});

// Usage
<CollaborationRequest 
  projectId={123}
  isOwner={false}
/>
```

## Notification Components

### NotificationCenter

Dropdown for displaying and managing notifications.

```tsx
// Props
interface NotificationCenterProps {
  initialCount?: number;
}

// State (React Query + WebSocket)
const { data: notifications, isLoading } = useQuery({
  queryKey: ['notifications'],
  queryFn: () => notificationService.getNotifications()
});

// WebSocket for real-time updates
useWebSocket((data) => {
  if (data.type === 'notification') {
    // Add notification to state
  }
});

// Usage
<NotificationCenter initialCount={3} />
```

### NotificationItem

Individual notification display component.

```tsx
// Props
interface NotificationItemProps {
  notification: Notification;
  onRead: () => void;
  onDelete: () => void;
}

// Usage
<NotificationItem 
  notification={notification}
  onRead={handleMarkAsRead}
  onDelete={handleDelete}
/>
```

### NotificationBadge

Badge showing unread notification count.

```tsx
// Props
interface NotificationBadgeProps {
  count: number;
  maxCount?: number;
}

// Usage
<NotificationBadge count={5} maxCount={99} />
```

## Search Components

### SearchBar

Input component for search functionality.

```tsx
// Props
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  initialQuery?: string;
}

// State
const [query, setQuery] = useState(initialQuery || '');
const debouncedQuery = useDebounce(query, 300);

useEffect(() => {
  if (debouncedQuery) {
    onSearch(debouncedQuery);
  }
}, [debouncedQuery, onSearch]);

// Usage
<SearchBar 
  onSearch={handleSearch}
  placeholder="Search users, posts, projects..."
  initialQuery=""
/>
```

### SearchFilters

Component for filtering search results.

```tsx
// Props
interface SearchFiltersProps {
  filters: SearchFilters;
  onFilterChange: (filters: SearchFilters) => void;
}

// Usage
<SearchFilters 
  filters={{ type: 'all', dateRange: 'anytime', sort: 'relevance' }}
  onFilterChange={handleFilterChange}
/>
```

### SearchResults

Display categorized search results.

```tsx
// Props
interface SearchResultsProps {
  results: SearchResultsData;
  isLoading: boolean;
  onLoadMore: () => void;
  hasMore: boolean;
}

// Usage
<SearchResults 
  results={searchResults}
  isLoading={isLoading}
  onLoadMore={fetchNextPage}
  hasMore={hasNextPage}
/>
```

## Form Components

### SkillSelector

Multi-select component for choosing skills from a predefined list.

```tsx
// Props
interface SkillSelectorProps {
  value: Skill[];
  onChange: (skills: Skill[]) => void;
  maxItems?: number;
}

// State
const [searchQuery, setSearchQuery] = useState('');
const { data: availableSkills, isLoading } = useQuery({
  queryKey: ['skills', searchQuery],
  queryFn: () => skillService.searchSkills(searchQuery)
});

// Usage
<SkillSelector 
  value={selectedSkills}
  onChange={setSelectedSkills}
  maxItems={10}
/>
```

### LanguageSelector

Dropdown component for selecting programming languages.

```tsx
// Props
interface LanguageSelectorProps {
  value: string | null;
  onChange: (language: string | null) => void;
}

// State
const { data: languages, isLoading } = useQuery({
  queryKey: ['programming-languages'],
  queryFn: () => languageService.getLanguages()
});

// Usage
<LanguageSelector 
  value={selectedLanguage}
  onChange={setSelectedLanguage}
/>
```

### ImageUploader

Component for uploading and previewing images.

```tsx
// Props
interface ImageUploaderProps {
  value: File | string | null;
  onChange: (file: File | null) => void;
  previewUrl?: string;
  accept?: string;
  maxSize?: number;
}

// State
const [preview, setPreview] = useState<string | null>(
  typeof value === 'string' ? value : previewUrl || null
);

// Usage
<ImageUploader 
  value={profileImage}
  onChange={handleImageChange}
  accept="image/*"
  maxSize={5 * 1024 * 1024} // 5MB
/>
```

## Feed Components

### FeedFilters

Component for filtering the user's feed.

```tsx
// Props
interface FeedFiltersProps {
  activeFilter: 'latest' | 'trending' | 'following';
  onChange: (filter: 'latest' | 'trending' | 'following') => void;
}

// Usage
<FeedFilters 
  activeFilter="latest"
  onChange={setActiveFilter}
/>
```

### FeedItem

Wrapper component that determines the type of content to display in the feed.

```tsx
// Props
interface FeedItemProps {
  item: FeedItem;
}

// Usage
<FeedItem item={feedItem} />
```

### PostComposer

Input component for creating a new post directly from the feed.

```tsx
// Props
interface PostComposerProps {
  onSubmit: (data: PostFormData) => void;
  placeholder?: string;
}

// State
const [isExpanded, setIsExpanded] = useState(false);
const [attachCode, setAttachCode] = useState(false);

// Usage
<PostComposer 
  onSubmit={handleCreatePost}
  placeholder="What's on your mind?"
/>
```

### TrendingTopics

Component displaying currently trending topics or hashtags.

```tsx
// Props
interface TrendingTopicsProps {
  limit?: number;
  onTopicClick?: (topic: string) => void;
}

// State (React Query)
const { data: topics, isLoading } = useQuery({
  queryKey: ['trending-topics'],
  queryFn: () => topicService.getTrendingTopics(limit)
});

// Usage
<TrendingTopics 
  limit={5}
  onTopicClick={(topic) => navigateToSearch(topic)}
/>
```

## Utility Components

### CodeEditor

Component for writing and editing code with syntax highlighting.

```tsx
// Props
interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: string;
  placeholder?: string;
}

// Usage
<CodeEditor 
  value={codeSnippet}
  onChange={setCodeSnippet}
  language="javascript"
  placeholder="// Write your code here"
/>
```

### ErrorBoundary

Component that catches JavaScript errors in child components.

```tsx
// Props
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback: React.ReactNode | ((error: Error) => React.ReactNode);
}

// Usage
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

### LoadingSpinner

Customizable loading indicator.

```tsx
// Props
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  text?: string;
}

// Usage
<LoadingSpinner 
  size="md"
  color="primary"
  text="Loading..."
/>
```

### InfiniteScroll

Component for implementing infinite scrolling in lists.

```tsx
// Props
interface InfiniteScrollProps {
  children: React.ReactNode;
  loadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  loader?: React.ReactNode;
  threshold?: number;
}

// Usage
<InfiniteScroll
  loadMore={fetchNextPage}
  hasMore={hasNextPage}
  isLoading={isFetchingNextPage}
  loader={<LoadingSpinner size="sm" />}
  threshold={300}
>
  {items.map(item => (
    <FeedItem key={item.id} item={item} />
  ))}
</InfiniteScroll>
```

## Component Relationships

### Authentication Flow

```
AuthProvider
└── App
    ├── LoginForm → useAuth.login → API → redirect
    ├── RegisterForm → useAuth.register → API → redirect
    └── ProtectedRoute → useAuth.isAuthenticated → redirect or render children
```

### Post Creation Flow

```
PostForm
├── LanguageSelector
│   └── (Programming languages from API)
├── CodeEditor (if code snippet included)
└── onSubmit → postService.createPost → API → redirect to post
```

### User Profile Flow

```
UserProfile
├── ProfileHeader
│   ├── UserAvatar
│   ├── UserStats
│   ├── FollowButton → API → update state
│   └── ProfileActions (if current user)
├── ProfileTabs
│   ├── UserPostsList
│   │   └── PostCard (repeated)
│   ├── UserProjectsList
│   │   └── ProjectCard (repeated)
│   └── UserSkillsList
│       └── SkillBadge (repeated)
└── UserActivity (recent actions)
```

### Feed Flow

```
FeedPage
├── FeedFilters → update query params → fetch new feed
├── PostComposer → open PostForm → create post → update feed
└── FeedList
    ├── InfiniteScroll → fetch more posts as user scrolls
    └── FeedItem (repeated)
        ├── PostCard
        │   ├── UserCard (author)
        │   ├── CodeSnippet (if has code)
        │   └── PostActions
        │       └── Like/Comment/Share buttons → API → update state
        └── ProjectCard (for project updates)
```

### Notification Flow

```
NotificationCenter
├── NotificationBadge → show unread count
├── WebSocket connection → real-time updates
└── NotificationList
    └── NotificationItem (repeated)
        ├── UserAvatar (of sender)
        ├── NotificationContent
        └── NotificationActions
            ├── Mark as read → API → update state
            └── Delete → API → update state
```

This architecture provides a comprehensive overview of the components, their properties, state, and the relationships between them. It serves as a blueprint for implementation and helps maintain consistency across the application. 