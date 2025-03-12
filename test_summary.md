# Test Summary

## Current Status

- **Security Tests**: All passing (19 tests passing, 3 skipped)
- **Overall Test Coverage**: 76%
- **Total Tests**: 171 (84 passing, 59 failing, 23 skipped, 5 errors)

## Main Issues to Fix

### URL Name Mismatches

The tests are using URL names that don't match the actual URL patterns in the project. For example:

- Tests use `post-list` but the actual URL name is `post-list-create`
- Tests use `post-comments` but the actual URL name is `comment-list-create`
- Tests use `user-profile` but the actual URL name is `user-me`

### Model Field Mismatches

The tests are using field names that don't match the actual model fields:

1. **Notification Model**:
   - Tests use `notification_type` but the actual field is `type`
   - Tests use `read` but the actual field is `is_read`

2. **Project Model**:
   - Tests use `repository_url` but the actual field is `repo_url`
   - Tests expect `ProjectCollaborator` to have a `created_at` field, but it has `joined_at`

3. **String Representation Mismatches**:
   - The string representation of models in tests doesn't match the actual implementation

### Missing Model Methods

Some tests expect methods that don't exist in the models:

- `CollaborationRequest.accept()`
- `CollaborationRequest.reject()`
- `CollaborationRequest.clean()` for validation

### API Response Mismatches

Some tests expect different API responses than what the actual API returns:

- Tests expect `400 Bad Request` for invalid collaboration requests, but the API returns `201 Created`
- Tests expect specific response formats that don't match the actual API responses

## Next Steps

1. Fix URL name mismatches in tests
2. Update tests to use the correct model field names
3. Add missing model methods for validation and actions
4. Fix API response expectations in tests
5. Add more tests to increase coverage to 100%

## Areas with Low Coverage

- `notifications/admin.py`: 38%
- `notifications/consumers.py`: 0%
- `notifications/routing.py`: 0%
- `posts/views/comments.py`: 62%
- `posts/views/posts.py`: 72%
- `posts/views/search.py`: 62%
- `projects/views/search.py`: 48%
- `socialistic/asgi.py`: 0%
- `socialistic/wsgi.py`: 0%
- `users/views/search.py`: 46% 