# 🚀 InventoryPro - Deployment Guide

## 📋 Overview

This guide explains how to deploy InventoryPro to production so your chatbot works outside of localhost.

The key issue: **Frontend can't connect to backend if it's hardcoded to localhost**

---

## 🎯 Architecture

```
┌─────────────────────────┐
│   Vercel/Netlify        │
│   (Next.js Frontend)    │
│   :3000                 │
└────────┬────────────────┘
         │ API calls to:
         │ NEXT_PUBLIC_API_URL
         ▼
┌─────────────────────────────┐
│   Railway/Render/VPS        │
│   (FastAPI Backend)         │
│   :8001                     │
│                             │
│ PostgreSQL (Supabase)       │
└─────────────────────────────┘
```

---

## ✅ Deployment Steps

### Step 1️⃣: Deploy Backend First

Choose one option:

#### Option A: **Railway.app** (Easiest)

```bash
# 1. Sign up at railway.app
# 2. Connect GitHub repository
# 3. Create new service → Python
# 4. Set environment variables:

SUPABASE_URL=https://grkfoepzoqhloxanexmb.supabase.co
SUPABASE_SERVICE_KEY=your_key_here
OPENROUTER_API_KEY=sk-or-v1-your_key_here
```

After deploy, you'll get a URL like: `https://inventorypro-api.railway.app`

#### Option B: **Render.com**

```bash
# 1. Sign up at render.com
# 2. New Web Service → Connect GitHub
# 3. Build command: pip install -r backend/requirements.txt
# 4. Start command: cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001
# 5. Add environment variables (same as above)
```

Get URL like: `https://inventorypro-api.onrender.com`

#### Option C: **VPS (Digital Ocean, Linode, AWS)**

```bash
# 1. SSH into server
# 2. Clone repository
# 3. Set up systemd service for backend
# 4. Set up nginx reverse proxy
# 5. Get URL like: https://api.yourdomain.com
```

---

### Step 2️⃣: Update Frontend Environment

After getting backend URL, set `NEXT_PUBLIC_API_URL` in your deployment:

#### For Vercel:

1. Go to your Vercel project
2. Settings → Environment Variables
3. Add new variable:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://your-backend-url.com (from Step 1)
   Environments: Production
   ```
4. Redeploy

#### For Netlify:

1. Go to your Netlify project
2. Site settings → Build & deploy → Environment
3. Add new variable:
   ```
   Key: NEXT_PUBLIC_API_URL
   Value: https://your-backend-url.com
   ```
4. Trigger rebuild

---

### Step 3️⃣: Deploy Frontend

#### For Vercel (Recommended)

```bash
# Frontend automatically deploys from GitHub
# Just push to main branch
git push origin main
```

Vercel auto-deploys. Your site will be at: `https://your-project.vercel.app`

#### For Netlify

```bash
# Push to GitHub and Netlify auto-deploys
# Or manually deploy:
npm run build
netlify deploy --prod --dir=.next
```

---

## ✅ Verify Deployment

After both frontend and backend are deployed:

### Test 1: Backend Health

```bash
curl https://your-backend-url.com/api/health
# Should return:
# {"status": "healthy", "service": "InventoryPro Chatbot"}
```

### Test 2: Frontend Loads

Open: `https://your-frontend-url.com`

Should load without errors.

### Test 3: Chatbot Works

1. Click chat bubble
2. Send a message
3. Should get response from backend

Check browser DevTools (F12) → Network tab:
- Look for `/api/chat` request
- Status should be `200`
- Response should have `message` field

---

## 🔴 Troubleshooting Deployment

### Issue: "Chat request failed" in production

**Cause:** `NEXT_PUBLIC_API_URL` not set correctly

**Fix:**
```bash
# Check what URL frontend is using
# In browser console, run:
console.log(process.env.NEXT_PUBLIC_API_URL)

# Should show your backend URL, not localhost
```

Then verify environment variable is set in your deployment platform.

### Issue: Backend returns 401/403

**Cause:** `OPENROUTER_API_KEY` not set

**Fix:** Add to backend environment variables:
```
OPENROUTER_API_KEY=sk-or-v1-your_actual_key
```

### Issue: CORS errors

**Cause:** Backend not configured for your frontend domain

**Fix:** Backend already has `CORS enabled for "*"` in code. If still failing:

1. Check backend is running: `curl https://your-backend-url.com/api/health`
2. Check frontend URL in environment variables
3. Check browser console for exact error

### Issue: Backend crashes on startup

**Cause:** Missing environment variables or dependencies

**Fix:**
```bash
# Verify requirements are installed
pip install -r backend/requirements.txt

# Check .env file has all variables:
echo $OPENROUTER_API_KEY
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_KEY
```

---

## 📋 Deployment Checklist

### Backend
- [ ] Code committed to GitHub
- [ ] Deployed to Railway/Render/VPS
- [ ] Environment variables set:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_SERVICE_KEY`
  - [ ] `OPENROUTER_API_KEY`
- [ ] Health check works: `curl https://backend-url/api/health` returns 200
- [ ] Backend URL copied (e.g., `https://api.yourdomain.com`)

### Frontend
- [ ] Code committed to GitHub
- [ ] `NEXT_PUBLIC_API_URL` environment variable set to backend URL
- [ ] Deployed to Vercel/Netlify
- [ ] Chatbot responds to messages

---

## 🆘 Quick Fixes

| Error | Fix |
|-------|-----|
| `ERR_CONNECTION_REFUSED` in browser | Set `NEXT_PUBLIC_API_URL` correctly |
| Backend shows 500 error | Check `OPENROUTER_API_KEY` Environment variable |
| Chatbot doesn't respond | Check Network tab → `/api/chat` response status |
| CORS errors | Backend has CORS enabled; check if backend is running |

---

## 📞 Help

If deployment still fails:

1. **Share your:**
   - Frontend URL
   - Backend URL
   - Browser console error (F12)
   - Network tab response for `/api/chat` request

2. **Check logs:**
   - Vercel: Deployments → Function logs
   - Render: Logs section
   - VPS: `journalctl -u inventorypro-backend -f`

---

## 🎉 Success!

Once deployed:
- Frontend: `https://your-frontend.vercel.app`
- Backend: `https://your-backend.railway.app`
- Chatbot works from anywhere! 🚀
