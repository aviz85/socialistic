# איפיון מערכת - רשת חברתית למתכנתים

## טכנולוגיות
- Django 5.0
- Django Rest Framework (DRF)
- JWT לאותנטיקציה
- PostgreSQL
- Redis (עבור caching ו-real-time features)

## מודלים

### User
- username (unique)
- email (unique)
- password (מוצפן)
- full_name
- bio
- profile_image
- github_profile (אופציונלי)
- stackoverflow_profile (אופציונלי)
- skills (ManyToMany לטבלת Skills)
- created_at
- last_login

### Post
- author (ForeignKey to User)
- content
- code_snippet (אופציונלי)
- programming_language (ForeignKey to ProgrammingLanguage)
- created_at
- updated_at
- likes (ManyToMany to User)
- comments (OneToMany to Comment)

### Comment
- author (ForeignKey to User)
- post (ForeignKey to Post)
- content
- created_at
- updated_at
- likes (ManyToMany to User)

### Project
- creator (ForeignKey to User)
- title
- description
- repo_url
- tech_stack (ManyToMany to Skills)
- collaborators (ManyToMany to User)
- created_at
- updated_at

### Skills
- name
- category (e.g., frontend, backend, devops)

### ProgrammingLanguage
- name
- icon

### Follow
- follower (ForeignKey to User)
- following (ForeignKey to User)
- created_at

### Notification
- recipient (ForeignKey to User)
- sender (ForeignKey to User)
- type (like, comment, follow, etc.)
- content
- read
- created_at

## Endpoints API

### אותנטיקציה
```
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
POST /api/auth/token/refresh/
GET /api/auth/me/
PUT /api/auth/me/
```

### משתמשים
```
GET /api/users/
GET /api/users/{id}/
GET /api/users/{id}/posts/
GET /api/users/{id}/projects/
POST /api/users/{id}/follow/
DELETE /api/users/{id}/unfollow/
GET /api/users/{id}/followers/
GET /api/users/{id}/following/
```

### פוסטים
```
GET /api/posts/
POST /api/posts/
GET /api/posts/{id}/
PUT /api/posts/{id}/
DELETE /api/posts/{id}/
POST /api/posts/{id}/like/
DELETE /api/posts/{id}/unlike/
GET /api/posts/{id}/comments/
POST /api/posts/{id}/comments/
```

### פרויקטים
```
GET /api/projects/
POST /api/projects/
GET /api/projects/{id}/
PUT /api/projects/{id}/
DELETE /api/projects/{id}/
POST /api/projects/{id}/collaborate/
DELETE /api/projects/{id}/leave/
```

### התראות
```
GET /api/notifications/
PUT /api/notifications/{id}/read/
DELETE /api/notifications/{id}/
```

### חיפוש
```
GET /api/search/users/
GET /api/search/posts/
GET /api/search/projects/
```

## הרשאות

### Anonymous
- צפייה בפרופילים ציבוריים
- צפייה בפוסטים ציבוריים
- צפייה בפרויקטים ציבוריים
- הרשמה והתחברות

### Authenticated
- כל פעולות ה-CRUD על התוכן שלהם
- לייקים ותגובות
- מעקב אחרי משתמשים אחרים
- הצטרפות לפרויקטים
- קבלת התראות

## אבטחה
- שימוש ב-JWT לאותנטיקציה
- CSRF protection
- Rate limiting
- Input validation
- XSS protection
- SQL injection protection

## Caching
- Redis עבור:
  - User sessions
  - Popular posts
  - User feed
  - Search results

## Real-time Features
- WebSocket עבור:
  - התראות בזמן אמת
  - עדכוני סטטוס
  - צ'אט בין משתמשים

## Pagination
- Cursor-based pagination עבור:
  - רשימות פוסטים
  - תוצאות חיפוש
  - התראות
  - תגובות

## תצורות סביבה
- Development
- Staging
- Production

## מערכת Logging
- Django logging
- Error tracking
- Performance monitoring
- User activity tracking

## תהליכי Background
- Celery עבור:
  - שליחת מיילים
  - עיבוד תמונות
  - ניתוח קוד
  - יצירת התראות
  - ניקוי מידע ישן 