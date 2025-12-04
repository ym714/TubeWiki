---
marp: true
theme: default
paginate: true
header: "TubeWiki Current Issues Report"
footer: "2025-12-03"
---

# TubeWiki Current Issues Report

## Overview

### 🔴 Active Issues
1. **QStash Publishing Error**
   - Summary generation fails with "Failed to queue job"
   - Status: **Critical** (Blocks core functionality)

### 🟢 Resolved Issues
1. **Database Schema Mismatch**
   - `notes` table missing `notion_url` column
   - Status: **Fixed**
2. **Extension API Connection**
   - "Failed to fetch" (CORS/Localhost)
   - Status: **Fixed**

---

# 🔴 Active Issue: QStash Error

## Error Details
- **Message**: `Failed to queue job`
- **Log**: `Client error '410 Gone' for url 'https://qstash.upstash.io/v1/publish/http://localhost:8001'`

## Root Cause
- The Core API is trying to send a job to QStash (Cloud Service).
- The destination URL is set to `http://localhost:8001` (Worker Service).
- **Problem**: QStash servers cannot access your local machine's `localhost`.

## Solution Options
1. **Use ngrok (Recommended for Dev)**
   - Expose Worker (`localhost:8001`) to the internet.
   - Update `WORKER_URL` in `.env` to the ngrok URL.
2. **Local Bypass**
   - Modify code to skip QStash and call Worker directly when running locally.

---

# 🟢 Resolved: Database Schema

## Problem
- **Error**: `sqlalchemy.exc.OperationalError: table notes has no column named notion_url`
- **Cause**: The SQLite database file (`test.db`) was created with an older schema and didn't match the current `Note` model.

## Fix Implemented
- Updated `core/main.py` to run `init_db()` on startup.
- Deleted the old `test.db` file.
- **Result**: Database tables are now correctly recreated with the latest schema on startup.

---

# 🟢 Resolved: API Connection

## Problem
- **Error**: `TypeError: Failed to fetch` in Chrome Extension.
- **Cause**: Chrome Extension did not have permission to access `http://localhost:8000`.

## Fix Implemented
- Updated `manifest.json`:
  ```json
  "host_permissions": [
    ...,
    "http://localhost:8000/*"
  ]
  ```
- **Result**: Extension can now successfully communicate with the Backend API.
