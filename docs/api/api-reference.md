# TubeWiki Core API Reference

## Overview
TubeWiki Core API provides endpoints for managing YouTube video summaries (Notes) and handling payments.

## Base URL
`http://localhost:8000/api/v1`

## Authentication
All endpoints require a valid Bearer token (Supabase JWT) in the `Authorization` header.
`Authorization: Bearer <token>`

## Endpoints

### Notes

#### Create Note
Create a new note (summary job) for a YouTube video.

- **URL**: `/notes`
- **Method**: `POST`
- **Status Code**: `202 Accepted`
- **Request Body**:
  ```json
  {
    "video_url": "https://www.youtube.com/watch?v=...",
    "preset": "default",
    "options": {}
  }
  ```
- **Response**:
  ```json
  {
    "message": "Job accepted",
    "note_id": "123",
    "status": "PENDING"
  }
  ```

#### Get Note
Get details of a specific note.

- **URL**: `/notes/{note_id}`
- **Method**: `GET`
- **Status Code**: `200 OK`
- **Response**:
  ```json
  {
    "id": 123,
    "user_id": "user_123",
    "video_url": "https://www.youtube.com/watch?v=...",
    "title": "Video Title",
    "content": "# Summary...",
    "status": "COMPLETED",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:05:00Z"
  }
  ```

#### Get Note by URL
Get a note by YouTube video URL.

- **URL**: `/notes/by-url/?video_url=...`
- **Method**: `GET`
- **Status Code**: `200 OK`
- **Response**: Same as Get Note.

### Health Check

#### Healthz
Check API health status.

- **URL**: `/healthz` (Root level, not under /api/v1)
- **Method**: `GET`
- **Status Code**: `200 OK`
- **Response**:
  ```json
  {
    "status": "ok",
    "service": "core-api",
    "version": "1.0.0"
  }
  ```
