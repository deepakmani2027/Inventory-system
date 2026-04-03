# 🐛 InventoryPro Chatbot - Debugging Guide

## ❌ Problem: "Chat request failed" - 500 Error

### 🔍 Root Causes & Solutions

---

## Issue 1: Backend Not Running

### Symptoms
- Frontend gets: `connection refused` or `localhost:8001 refused to connect`
- Browser console shows: `Failed to fetch`

### Solution

```bash
# Terminal 1: Start Backend
cd backend
source venv/bin/activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Started server process
```

---

## Issue 2: httpx Not Installed

### Symptoms
- Backend shows: `ModuleNotFoundError: No module named 'httpx'`
- Error happens when you send a chat message

### Solution

```bash
# In backend directory with venv activated
pip install httpx>=0.24.0
```

Verify:
```bash
python -c "import httpx; print('✅ httpx installed')"
```

---

## Issue 3: OPENROUTER_API_KEY Not Set

### Symptoms
- Backend error: `OPENROUTER_API_KEY not configured`
- Chat endpoint returns 500 with that message

### Solution

```bash
# Edit backend/.env
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
```

Get your key:
1. Visit https://openrouter.ai
2. Go to Settings → Keys
3. Copy your API key (starts with `sk-or-v1-`)

---

## Issue 4: Wrong Backend Requirements

### Symptoms
- Missing dependencies errors
- Import errors on startup

### Solution

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Current requirements should include:
- ✅ fastapi>=0.100.0
- ✅ uvicorn>=0.23.0
- ✅ httpx>=0.24.0
- ✅ python-dotenv>=1.0.0
- ✅ supabase>=2.0.0
- ✅ pydantic>=2.0.0

---

## 🧪 Testing

### Test 1: Backend Health Check

```bash
curl http://localhost:8001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "InventoryPro Chatbot"
}
```

### Test 2: Chat Endpoint

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What items are in stock?"}
    ]
  }'
```

Expected response:
```json
{
  "message": "Here are the current items in stock...",
  "sessionId": "..."
}
```

### Test 3: Browser DevTools

1. Open http://localhost:3000
2. Press F12 (DevTools)
3. Go to Console tab
4. Send a chat message
5. Check Network tab for `/api/chat` request

Look for:
- Status: 200 (success)
- Response body has `message` and `sessionId`

---

## 🔴 Common Error Messages & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `connection refused` | Backend not running | `bash start_backend.sh` |
| `ModuleNotFoundError: httpx` | httpx not installed | `pip install httpx` |
| `OPENROUTER_API_KEY not configured` | Missing API key in .env | Set in `backend/.env` |
| `401 Unauthorized` | Invalid OpenRouter key | Check key starts with `sk-or-v1-` |
| `400 Bad Request` | Wrong message format | Ensure `"role"` and `"content"` fields |
| `504 Timeout` | OpenRouter API slow | Try again or check limit |

---

## 📋 Checklist Before Asking for Help

- [ ] Backend is running (`bash start_backend.sh`)
- [ ] Frontend is running (`npm run dev`)
- [ ] `curl http://localhost:8001/api/health` returns 200
- [ ] `backend/.env` has `OPENROUTER_API_KEY=sk-or-v1-...`
- [ ] No missing Python modules (`pip install -r requirements.txt`)
- [ ] Browser DevTools shows `/api/chat` request (check Network tab)
- [ ] No errors in terminal when sending chat message

---

## 🛠️ Complete Fresh Start

If nothing works, do a complete reset:

```bash
# Remove virtual environment
rm -rf backend/venv

# Reinstall everything
bash setup.sh

# Start backend
bash start_backend.sh

# In another terminal, start frontend
npm run dev
```

---

## 📞 If Still Broken

Check terminal output for:
1. **Backend terminal** - What error appears when you send a message?
2. **Browser console (F12)** - What error appears?
3. **Network tab** - What's the response status and body?

Share those and we can debug further!
