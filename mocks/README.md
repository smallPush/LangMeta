# Meta Graph API Mocks

This directory contains mock JSON responses for the Meta Graph API. These mocks demonstrate the expected structure and format returned by the API for different operations.

## Available Mocks

### 1. `get_posts.json`
- **Description**: Mock response for retrieving a list of posts from an account.
- **Meta Graph API Path**: `GET /{account_id}/posts`
- **Format**: Returns a JSON object with a `data` array containing post objects (id, message, created_time) and a `paging` object for pagination.

### 2. `get_comments.json`
- **Description**: Mock response for retrieving a list of comments on a specific post.
- **Meta Graph API Path**: `GET /{post_id}/comments`
- **Format**: Returns a JSON object with a `data` array containing comment objects (id, message, created_time) and a `paging` object for pagination.

### 3. `get_likes.json`
- **Description**: Mock response for retrieving a list of likes on a specific object (post or comment).
- **Meta Graph API Path**: `GET /{object_id}/likes`
- **Format**: Returns a JSON object with a `data` array containing user objects (id, name) and a `paging` object for pagination.

### 4. `post_comment.json`
- **Description**: Mock response for successfully creating a new comment on an object.
- **Meta Graph API Path**: `POST /{object_id}/comments`
- **Format**: Returns a JSON object containing the `id` of the newly created comment.

### 5. `like_object.json`
- **Description**: Mock response for successfully liking a specific object.
- **Meta Graph API Path**: `POST /{object_id}/likes`
- **Format**: Returns a JSON object indicating success (`"success": true`).
