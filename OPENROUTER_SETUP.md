# OpenRouter Integration Setup Guide

Your InventoryPro Chatbot now uses **OpenRouter API** for intelligent LLM-powered conversations.

## 🚀 What Changed?

| Component | Old | New |
|-----------|-----|-----|
| **LLM Provider** | EmergentIntegrations | OpenRouter |
| **API Key** | `EMERGENT_LLM_KEY` | `OPENROUTER_API_KEY` |
| **Backend** | `emergentintegrations` lib | `httpx` (native API calls) |
| **Model** | Custom | `openai/gpt-4o-mini` |

## 📋 Prerequisites

1. **OpenRouter Account** - Sign up at https://openrouter.ai
2. **API Key** - Get it from https://openrouter.ai/settings/keys

## 🔧 Configuration

### Step 1: Get OpenRouter API Key

1. Visit https://openrouter.ai/settings/keys
2. Click "Create New Key"
3. Copy your API key (starts with `sk-or-v1-...`)

### Step 2: Set Environment Variables

Create `/backend/.env`:

```bash
SUPABASE_URL=https://grkfoepzoqhloxanexmb.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_key_here
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
```

Also update `/app/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://grkfoepzoqhloxanexmb.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_key_here
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
```

### Step 3: Install Dependencies

```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
npm install
```

## 🏃 Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Started reloader process
```

### Start Frontend

```bash
# In project root
npm run dev
```

**Output:**
```
▲ Next.js X.X.X
- Local:        http://localhost:3000
- Ready in Xms
```

### Visit Application

Open http://localhost:3000 in your browser

All tests passed! ✅ The chatbot should now respond to your questions using OpenRouter's models.

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Send chat message |

### Example Request

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What items are in stock?"}
    ],
    "sessionId": "session-123"
  }'
```

### Example Response

```json
{
  "message": "Based on the current inventory data, here are the items in stock...",
  "sessionId": "session-123"
}
```

## 📊 Backend Implementation

The backend uses **direct HTTP calls** to OpenRouter API:

```python
# backend/server.py

async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://inventorypro.local",
            "X-OpenRouter-Title": "InventoryPro Chatbot",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        },
        timeout=30.0
    )
```

## 🛠️ Configuration Options

### Change LLM Model

Edit `/backend/server.py`:

```python
OPENROUTER_MODEL = "openai/gpt-4o"  # Upgrade to GPT-4
# or
OPENROUTER_MODEL = "anthropic/claude-3-sonnet"  # Use Claude
# or
OPENROUTER_MODEL = "google/gemini-2.0-flash"  # Use Gemini
```

See all available models: https://openrouter.ai/models

### Adjust Response Generation

```python
# backend/server.py - in the /api/chat endpoint

json={
    "temperature": 0.5,      # Lower = more deterministic (0-2)
    "max_tokens": 2000,      # Increase for longer responses
    "top_p": 0.9,            # Nucleus sampling
}
```

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.10+

# Try creating fresh venv
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### API key error

```
Error: OPENROUTER_API_KEY not configured
```

**Fix:** Ensure `backend/.env` contains your OpenRouter API key

```bash
cat backend/.env | grep OPENROUTER_API_KEY
```

### Chat not responding

1. Check backend is running:
   ```bash
   curl http://localhost:8001/api/health
   ```

2. Check API key validity:
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" \
        https://openrouter.ai/api/v1/models
   ```

3. Check logs for errors - look for error messages in terminal

### Rate limits / Account issues

Check your OpenRouter account:
- https://openrouter.ai/account/billing/overview
- Verify account is active and has credits
- Check API key hasn't been revoked

## 📚 OpenRouter Documentation

- **Main Docs**: https://openrouter.ai/docs
- **Models**: https://openrouter.ai/models
- **API Reference**: https://openrouter.ai/docs/api/v1
- **Pricing**: https://openrouter.ai/pricing
- **Settings**: https://openrouter.ai/settings/keys

## 🔐 Security

- ✅ `.env.local` and `.env` are in `.gitignore` - secrets won't be committed
- ✅ API keys are environment variables - never hardcoded
- ✅ `.env.example` contains placeholders for reference
- ✅ Production: Use secure secret management (Vercel Secrets, AWS Secrets Manager, etc.)

## 📊 Performance Tips

1. **Cache responses** - Store chat history in database
2. **Use cheaper models** - Try `gpt-3.5-turbo` in production
3. **Batch requests** - Group multiple queries when possible
4. **Monitor costs** - Check OpenRouter dashboard regularly

## ✅ Verification

Run this to verify everything is working:

```bash
# Backend health check
curl http://localhost:8001/api/health | jq .

# Test chat
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "sessionId": "test"
  }' | jq .message
```

## 🚢 Deployment

### Vercel (Frontend)

```bash
npm run build
```

### Railway / Render (Backend)

Add environment variables:
- `OPENROUTER_API_KEY=sk-or-v1-...`
- `SUPABASE_URL=...`
- `SUPABASE_SERVICE_KEY=...`

## 📞 Support

- **OpenRouter Support**: https://openrouter.ai/support
- **Project Issues**: Check GitHub issues
- **Backend Logs**: Check terminal for error messages

---

**Happy coding!** 🎉

Your chatbot is now powered by OpenRouter's best-in-class LLMs!
