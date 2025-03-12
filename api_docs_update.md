# API Documentation Update Report

Generated on: 2025-03-12 08:28:35

## Summary

- Total endpoints tested: 11
- Endpoints passed: 11
- Endpoints failed: 0
- Endpoints skipped: 0

## Endpoints by Resource

### Auth

- ✅ **POST** `/api/auth/register/`
  - Response Status: 201
  - Response Schema:
```json
{
  "user": {
    "id": 27,
    "username": "testuser_1741760915",
    "email": "test_1741760915@example.com",
    "full_name": "Test User",
    "bio": "",
    "profile_image": null,
    "github_profile": "",
    "stackoverflow_profile": "",
    "skills": [],
    "followers_count": 0,
    "following_count": 0,
    "is_following": false,
    "created_at": "2025-03-12T06:28:35.173788Z"
  },
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0MTg0NzMxNSwiaWF0IjoxNzQxNzYwOTE1LCJqdGkiOiJhZmEyZGFlODA1MDA0OTkzOTY3NThjNzdhYTgzNzY0NSIsInVzZXJfaWQiOjI3fQ.4i5vCFBAU16eN1pUsrf57TLzrkUL5yJShAkpMW4vObk",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxNzY0NTE1LCJpYXQiOjE3NDE3NjA5MTUsImp0aSI6ImEyMTQ2ZWY3MzZmYTRjOTI4N2QzMjE5ZTEyNGE5NGI1IiwidXNlcl9pZCI6Mjd9.CGdLbgZKf3n20HN0uQg-pUnFzgtB5NTVclYaRqFxsYk"
}
```
- ✅ **POST** `/api/auth/login/`
  - Response Status: 200
  - Response Schema:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0MTg0NzMxNSwiaWF0IjoxNzQxNzYwOTE1LCJqdGkiOiI5MzNiYjRjN2MzYTc0MmViODBhYjI1NzVjODdhZGVmNyIsInVzZXJfaWQiOjI3fQ.TkgpmANR8QoEoS-PemW0C-7ud6Iv0h6-VJYJ1oEQuoo",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxNzY0NTE1LCJpYXQiOjE3NDE3NjA5MTUsImp0aSI6IjRlZmNlZmY5NTJmODQzZTc5NGZkMWIyYmI4MTE5NzcwIiwidXNlcl9pZCI6Mjd9.G_3kZz4DyQCg5pFZdQNZyHiDkbOq2ysjQVNllNLXGxI",
  "user": {
    "id": 27,
    "username": "testuser_1741760915",
    "email": "test_1741760915@example.com",
    "full_name": "Test User",
    "bio": "",
    "profile_image": null,
    "github_profile": "",
    "stackoverflow_profile": "",
    "skills": [],
    "followers_count": 0,
    "following_count": 0,
    "is_following": false,
    "created_at": "2025-03-12T06:28:35.173788Z"
  }
}
```
- ✅ **GET** `/api/auth/me/`
  - Response Status: 200
  - Response Schema:
```json
{
  "id": 27,
  "username": "testuser_1741760915",
  "email": "test_1741760915@example.com",
  "full_name": "Test User",
  "bio": "",
  "profile_image": null,
  "github_profile": "",
  "stackoverflow_profile": "",
  "skills": [],
  "followers_count": 0,
  "following_count": 0,
  "is_following": false,
  "created_at": "2025-03-12T06:28:35.173788Z"
}
```

### Notifications

- ✅ **GET** `/api/notifications/`
  - Response Status: 200
  - Response Schema:
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```
- ✅ **GET** `/api/notifications/settings/`
  - Response Status: 200
  - Response Schema:
```json
{
  "email_likes": true,
  "email_comments": true,
  "email_follows": true,
  "email_mentions": true,
  "email_project_invites": true,
  "email_project_requests": true,
  "push_likes": true,
  "push_comments": true,
  "push_follows": true,
  "push_mentions": true,
  "push_project_invites": true,
  "push_project_requests": true
}
```
- ✅ **PUT** `/api/notifications/settings/`
  - Response Status: 200
  - Response Schema:
```json
{
  "email_likes": false,
  "email_comments": false,
  "email_follows": true,
  "email_mentions": true,
  "email_project_invites": true,
  "email_project_requests": true,
  "push_likes": true,
  "push_comments": true,
  "push_follows": true,
  "push_mentions": true,
  "push_project_invites": true,
  "push_project_requests": true
}
```

### Posts

- ✅ **POST** `/api/posts/`
  - Response Status: 201
  - Response Schema:
```json
{
  "id": 103,
  "author": {
    "id": 27,
    "username": "testuser_1741760915",
    "email": "test_1741760915@example.com",
    "full_name": "Test User",
    "bio": "",
    "profile_image": null,
    "github_profile": "",
    "stackoverflow_profile": "",
    "skills": [],
    "followers_count": 0,
    "following_count": 0,
    "is_following": false,
    "created_at": "2025-03-12T06:28:35.173788Z"
  },
  "content": "Test post content at 2025-03-12 08:28:35",
  "code_snippet": "print('Hello, world!')",
  "programming_language": null,
  "created_at": "2025-03-12T06:28:35.284332Z",
  "updated_at": "2025-03-12T06:28:35.284346Z",
  "likes_count": 0,
  "comments_count": 0,
  "is_liked": false
}
```
- ✅ **POST** `/api/posts/103/like/`
- ✅ **DELETE** `/api/posts/103/unlike/`
- ✅ **POST** `/api/posts/103/comments/`
  - Response Status: 201
  - Response Schema:
```json
{
  "id": 266,
  "author": {
    "id": 27,
    "username": "testuser_1741760915",
    "email": "test_1741760915@example.com",
    "full_name": "Test User",
    "bio": "",
    "profile_image": null,
    "github_profile": "",
    "stackoverflow_profile": "",
    "skills": [],
    "followers_count": 0,
    "following_count": 0,
    "is_following": false,
    "created_at": "2025-03-12T06:28:35.173788Z"
  },
  "content": "Test comment at 2025-03-12 08:28:35",
  "created_at": "2025-03-12T06:28:35.307935Z",
  "updated_at": "2025-03-12T06:28:35.307952Z",
  "likes_count": 0,
  "is_liked": false
}
```

### Projects

- ✅ **POST** `/api/projects/`
  - Response Status: 201
  - Response Schema:
```json
{
  "id": 49,
  "creator": {
    "id": 27,
    "username": "testuser_1741760915",
    "email": "test_1741760915@example.com",
    "full_name": "Test User",
    "bio": "",
    "profile_image": null,
    "github_profile": "",
    "stackoverflow_profile": "",
    "skills": [],
    "followers_count": 0,
    "following_count": 0,
    "is_following": false,
    "created_at": "2025-03-12T06:28:35.173788Z"
  },
  "title": "Test Project 2025-03-12 08:28:35",
  "description": "This is a test project created by the API tester",
  "repo_url": "https://github.com/test/test-project",
  "tech_stack": [],
  "status": "active",
  "created_at": "2025-03-12T06:28:35.325319Z",
  "updated_at": "2025-03-12T06:28:35.325337Z",
  "collaborators_count": 1,
  "is_collaborator": true,
  "collaborators": [
    {
      "id": 110,
      "user": {
        "id": 27,
        "username": "testuser_1741760915",
        "email": "test_1741760915@example.com",
        "full_name": "Test User",
        "bio": "",
        "profile_image": null,
        "github_profile": "",
        "stackoverflow_profile": "",
        "skills": [],
        "followers_count": 0,
        "following_count": 0,
        "is_following": false,
        "created_at": "2025-03-12T06:28:35.173788Z"
      },
      "role": "owner",
      "joined_at": "2025-03-12T06:28:35.326704Z"
    }
  ]
}
```

## Documentation Recommendations

✅ Documentation is up to date with the tested endpoints.

