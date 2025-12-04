---
marp: true
theme: default
paginate: true
header: "TubeWiki Current Problems Report"
footer: "2025-12-04"
---

# TubeWiki Current Problems Report

## 🚨 Critical Issues

### 1. API 404 Not Found (Active)
- **Symptom**: "API request failed with status 404" when clicking Notion button.
- **Cause**: The extension is sending requests to `/notes` instead of `/api/v1/notes`.
- **Status**: **Regression**. The fix was implemented but reverted by user.
- **Action Required**: Re-apply the fix in `extension/src/lib/api.ts` or update `.env`.

### 2. QStash Connection Error (Active)
- **Symptom**: "Failed to queue job" (500 Internal Server Error).
- **Log**: `Client error '410 Gone' for url 'https://qstash.upstash.io/v1/publish/http://localhost:8001'`
- **Cause**: QStash (Cloud) cannot connect to `localhost:8001` (Worker).
- **Action Required**: Use **ngrok** to expose the Worker service or implement a local bypass.

---

# ⚠️ Minor Issues

### 3. MetaMask Conflict
- **Symptom**: Console errors about "Ethereum provider".
- **Cause**: Conflict between multiple wallet extensions.
- **Impact**: Annoying logs, but does not affect TubeWiki functionality.
- **Action**: Ignore or disable conflicting extensions during development.

---

# Recommended Next Steps

1. **Fix API URL**: Update `extension/src/lib/api.ts` to ensure `/api/v1` is appended.
2. **Solve QStash Issue**:
   - **Option A**: Install `ngrok` and expose port 8001.
   - **Option B**: Modify backend to skip QStash when running locally.
