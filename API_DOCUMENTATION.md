# Socialistic API Documentation

## Overview

The Socialistic API provides endpoints for a developer social network platform. It allows users to create profiles, posts, projects, follow each other, and collaborate on projects.

## Base URL

All API endpoints are relative to: `http://localhost:8050/api`

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require authentication.

### Authentication Endpoints

#### Register a new user

- **URL**: `/auth/register/`
- **Method**: `POST`
- **Description**: API endpoint for user registration.
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "user@example.com",
    "full_name": "string",
    "password": "string",
    "confirm_password": "string"
  }
  ```
- **Response**: `201 Created`

#### Login

- **URL**: `/auth/login/`
- **Method**: `POST`
- **Description**: Custom JWT token view that returns user data with tokens.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "string"
  }
  ```
- **Response**: `201 Created`

#### Logout

- **URL**: `/auth/logout/`
- **Method**: `POST`
- **Description**: API endpoint for logout - blacklist the JWT token.
- **Response**: `201 Created`

#### Get Current User

- **URL**: `/auth/me/`
- **Method**: `GET`
- **Description**: API endpoint to get the authenticated user.
- **Response**: `200 OK`

#### Update Current User

- **URL**: `/auth/me/`
- **Method**: `PUT` or `PATCH`
- **Description**: API endpoint to update the authenticated user.
- **Request Body**:
  ```json
  {
    "username": "string",
    "full_name": "string",
    "bio": "string",
    "github_profile": "string",
    "stackoverflow_profile": "string"
  }
  ```
- **Response**: `200 OK`

#### Refresh Token

- **URL**: `/auth/token/refresh/`
- **Method**: `POST`
- **Description**: Takes a refresh type JSON web token and returns an access type JSON web token if the refresh token is valid.
- **Request Body**:
  ```json
  {
    "refresh": "string"
  }
  ```
- **Response**: `201 Created`

## Users

### User Endpoints

#### List Users

- **URL**: `/users/`
- **Method**: `GET`
- **Description**: API endpoint for listing users.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### Get User Profile

- **URL**: `/users/{id}/`
- **Method**: `GET`
- **Description**: API endpoint for retrieving a user.
- **Response**: `200 OK`

#### Get Current User Profile

- **URL**: `/users/me/`
- **Method**: `GET`
- **Description**: API endpoint to get the authenticated user.
- **Response**: `200 OK`

#### Update Current User Profile

- **URL**: `/users/me/`
- **Method**: `PUT` or `PATCH`
- **Description**: API endpoint to update the authenticated user.
- **Response**: `200 OK`

#### Follow a User

- **URL**: `/users/{id}/follow/`
- **Method**: `POST`
- **Description**: API endpoint for following a user.
- **Response**: `201 Created`

#### Unfollow a User

- **URL**: `/users/{id}/unfollow/`
- **Method**: `DELETE`
- **Description**: API endpoint for unfollowing a user.
- **Response**: `204 No Content`

#### List User's Followers

- **URL**: `/users/{id}/followers/`
- **Method**: `GET`
- **Description**: API endpoint for listing a user's followers.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### List User's Following

- **URL**: `/users/{id}/following/`
- **Method**: `GET`
- **Description**: API endpoint for listing users that a user is following.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### List User's Posts

- **URL**: `/users/{id}/posts/`
- **Method**: `GET`
- **Description**: API endpoint for listing a user's posts.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### List User's Projects

- **URL**: `/users/{id}/projects/`
- **Method**: `GET`
- **Description**: API endpoint for listing a user's projects.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

## Posts

### Post Endpoints

#### List Posts

- **URL**: `/posts/`
- **Method**: `GET`
- **Description**: API endpoint for listing posts.
- **Query Parameters**:
  - `cursor`: The pagination cursor value
- **Response**: `200 OK`

#### Create Post

- **URL**: `/posts/`
- **Method**: `POST`
- **Description**: API endpoint for creating posts.
- **Request Body**:
  ```json
  {
    "content": "string",
    "code_snippet": "string",
    "programming_language_id": 0
  }
  ```
- **Response**: `201 Created`

#### Get Post

- **URL**: `/posts/{id}/`
- **Method**: `GET`
- **Description**: API endpoint for retrieving a post.
- **Response**: `200 OK`

#### Update Post

- **URL**: `/posts/{id}/`
- **Method**: `PUT` or `PATCH`
- **Description**: API endpoint for updating a post.
- **Request Body**:
  ```json
  {
    "content": "string",
    "code_snippet": "string",
    "programming_language_id": 0
  }
  ```
- **Response**: `200 OK`

#### Delete Post

- **URL**: `/posts/{id}/`
- **Method**: `DELETE`
- **Description**: API endpoint for deleting a post.
- **Response**: `204 No Content`

#### Like Post

- **URL**: `/posts/{id}/like/`
- **Method**: `POST`
- **Description**: API endpoint for liking a post.
- **Response**: `201 Created`

#### Search Posts

- **URL**: `/posts/search/`
- **Method**: `GET`
- **Description**: API endpoint for searching posts.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

### Comment Endpoints

#### List Comments on Post

- **URL**: `/posts/{post_id}/comments/`
- **Method**: `GET`
- **Description**: API endpoint for listing comments on a post.
- **Query Parameters**:
  - `cursor`: The pagination cursor value
- **Response**: `200 OK`

#### Create Comment on Post

- **URL**: `/posts/{post_id}/comments/`
- **Method**: `POST`
- **Description**: API endpoint for creating comments on a post.
- **Request Body**:
  ```json
  {
    "content": "string"
  }
  ```
- **Response**: `201 Created`

#### Get Comment

- **URL**: `/posts/comments/{id}/`
- **Method**: `GET`
- **Description**: API endpoint for retrieving a comment.
- **Response**: `200 OK`

#### Update Comment

- **URL**: `/posts/comments/{id}/`
- **Method**: `PUT` or `PATCH`
- **Description**: API endpoint for updating a comment.
- **Request Body**:
  ```json
  {
    "content": "string"
  }
  ```
- **Response**: `200 OK`

#### Delete Comment

- **URL**: `/posts/comments/{id}/`
- **Method**: `DELETE`
- **Description**: API endpoint for deleting a comment.
- **Response**: `204 No Content`

#### Like Comment

- **URL**: `/posts/comments/{id}/like/`
- **Method**: `POST`
- **Description**: API endpoint for liking a comment.
- **Response**: `201 Created`

#### Unlike Comment

- **URL**: `/posts/comments/{id}/like/`
- **Method**: `DELETE`
- **Description**: API endpoint for unliking a comment.
- **Response**: `204 No Content`

## Projects

### Project Endpoints

#### List Projects

- **URL**: `/projects/`
- **Method**: `GET`
- **Description**: API endpoint for listing projects.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### Create Project

- **URL**: `/projects/`
- **Method**: `POST`
- **Description**: API endpoint for creating projects.
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "repo_url": "string",
    "tech_stack_ids": [0],
    "status": "active"
  }
  ```
- **Response**: `201 Created`

#### Get Project

- **URL**: `/projects/{id}/`
- **Method**: `GET`
- **Description**: API endpoint for retrieving a project.
- **Response**: `200 OK`

#### Update Project

- **URL**: `/projects/{id}/`
- **Method**: `PUT` or `PATCH`
- **Description**: API endpoint for updating a project.
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "repo_url": "string",
    "tech_stack_ids": [0],
    "status": "active"
  }
  ```
- **Response**: `200 OK`

#### Delete Project

- **URL**: `/projects/{id}/`
- **Method**: `DELETE`
- **Description**: API endpoint for deleting a project.
- **Response**: `204 No Content`

#### Request to Collaborate

- **URL**: `/projects/{id}/collaborate/`
- **Method**: `POST`
- **Description**: API endpoint for requesting to collaborate on a project.
- **Response**: `201 Created`

#### Leave Project

- **URL**: `/projects/{id}/leave/`
- **Method**: `DELETE`
- **Description**: API endpoint for leaving a project.
- **Response**: `204 No Content`

#### List Collaboration Requests

- **URL**: `/projects/collaboration-requests/`
- **Method**: `GET`
- **Description**: API endpoint for listing collaboration requests for projects created by the user.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### Respond to Collaboration Request

- **URL**: `/projects/collaboration-requests/{id}/respond/`
- **Method**: `POST`
- **Description**: API endpoint for responding to a collaboration request.
- **Response**: `201 Created`

## Notifications

### Notification Endpoints

#### List Notifications

- **URL**: `/notifications/`
- **Method**: `GET`
- **Description**: API endpoint for listing user notifications.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### Delete Notification

- **URL**: `/notifications/{id}/`
- **Method**: `DELETE`
- **Description**: API endpoint for deleting a notification.
- **Response**: `204 No Content`

#### Mark Notification as Read

- **URL**: `/notifications/{id}/read/`
- **Method**: `PUT`
- **Description**: API endpoint for marking a notification as read.
- **Response**: `200 OK`

#### Get Notification Settings

- **URL**: `/notifications/settings/`
- **Method**: `GET`
- **Description**: API endpoint for retrieving notification settings.
- **Response**: `200 OK`

#### Update Notification Settings

- **URL**: `/notifications/settings/`
- **Method**: `PUT` or `PATCH`
- **Description**: API endpoint for updating notification settings.
- **Request Body**:
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
- **Response**: `200 OK`

## Search

### Search Endpoints

#### Search Posts

- **URL**: `/search/posts/`
- **Method**: `GET`
- **Description**: API endpoint for searching posts.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### Search Projects

- **URL**: `/search/projects/`
- **Method**: `GET`
- **Description**: API endpoint for searching projects.
- **Query Parameters**:
  - `search`: A search term
  - `page`: Page number for pagination
- **Response**: `200 OK`

#### Search Users

- **URL**: `/search/users/`
- **Method**: `GET`
- **Description**: API endpoint for searching users.
- **Query Parameters**:
  - `search`: A search term
  - `page`: Page number for pagination
- **Response**: `200 OK`

## Programming Languages

### Programming Language Endpoints

#### List Programming Languages

- **URL**: `/programming-languages/`
- **Method**: `GET`
- **Description**: API endpoint to list all programming languages.
- **Query Parameters**:
  - `page`: Page number for pagination
- **Response**: `200 OK`

## Data Models

### User Model

```json
{
  "id": 0,
  "username": "string",
  "email": "user@example.com",
  "full_name": "string",
  "bio": "string",
  "profile_image": "uri",
  "github_profile": "uri",
  "stackoverflow_profile": "uri",
  "skills": [
    {
      "id": 0,
      "name": "string",
      "category": "frontend"
    }
  ],
  "followers_count": 0,
  "following_count": 0,
  "is_following": "boolean",
  "created_at": "datetime"
}
```

### Post Model

```json
{
  "id": 0,
  "author": {
    "id": 0,
    "username": "string",
    "profile_image": "uri"
  },
  "content": "string",
  "code_snippet": "string",
  "programming_language": {
    "id": 0,
    "name": "string",
    "icon": "uri"
  },
  "created_at": "datetime",
  "updated_at": "datetime",
  "likes_count": 0,
  "comments_count": 0,
  "is_liked": "boolean"
}
```

### Comment Model

```json
{
  "id": 0,
  "author": {
    "id": 0,
    "username": "string",
    "profile_image": "uri"
  },
  "content": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "likes_count": 0,
  "is_liked": "boolean"
}
```

### Project Model

```json
{
  "id": 0,
  "creator": {
    "id": 0,
    "username": "string",
    "profile_image": "uri"
  },
  "title": "string",
  "description": "string",
  "repo_url": "uri",
  "tech_stack": [
    {
      "id": 0,
      "name": "string",
      "category": "string"
    }
  ],
  "status": "active",
  "created_at": "datetime",
  "updated_at": "datetime",
  "collaborators_count": 0,
  "is_collaborator": "boolean"
}
```

### Notification Model

```json
{
  "id": 0,
  "recipient": 0,
  "sender": {
    "id": 0,
    "username": "string",
    "profile_image": "uri"
  },
  "type": "like",
  "text": "string",
  "is_read": false,
  "created_at": "datetime",
  "content_type": 0,
  "object_id": 0
}
```

### Skills Model

```json
{
  "id": 0,
  "name": "string",
  "category": "frontend"
}
```

### Programming Language Model

```json
{
  "id": 0,
  "name": "string",
  "icon": "uri"
}
``` 