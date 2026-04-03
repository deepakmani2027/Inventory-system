# InventoryPro AI Chatbot - PRD

## Original Problem Statement
Build a proper website chatbot for the InventoryPro website (https://inventory-hitk.vercel.app/) using Gemini/OpenAI API via Emergent LLM key, fetching data from Supabase database.

## Architecture

### Tech Stack
- **Frontend**: Next.js 16 with React, Tailwind CSS, shadcn/ui
- **Backend**: Python FastAPI with emergentintegrations library
- **LLM**: OpenAI GPT-4o-mini via Emergent Universal Key
- **Database**: Supabase (PostgreSQL)

### Components
1. **Chatbot UI** (`/app/components/chatbot/Chatbot.tsx`)
   - Floating chat bubble (bottom-right)
   - Chat window with messages
   - Suggested questions for quick start
   - Real-time loading indicators

2. **Next.js API Route** (`/app/app/api/chat/route.ts`)
   - Proxies requests to Python backend

3. **Python Backend** (`/app/backend/server.py`)
   - FastAPI service on port 8001
   - Fetches real-time inventory data from Supabase
   - Uses emergentintegrations for LLM calls
   - Provides context-aware responses

## User Personas
- **Admin**: Full access, manages users/categories/items
- **Salesman**: Billing, stock view, returns
- **Inventory Manager**: Restock, low stock alerts
- **Sales Manager**: Analytics, reports, trends

## Core Requirements (Static)
- [x] AI-powered chatbot with natural language understanding
- [x] Real-time inventory data integration
- [x] Context-aware responses about stock levels
- [x] Low stock alerts
- [x] Sales information queries
- [x] Platform navigation guidance

## What's Been Implemented (Jan 2026)
- [x] Floating chat bubble UI with smooth animations
- [x] Chat window with minimize/close functionality
- [x] Suggested questions feature
- [x] Real-time Supabase data fetching
- [x] GPT-4o-mini integration via Emergent key
- [x] Multi-turn conversation support
- [x] Low stock alerts with recommendations
- [x] Items/categories/sales queries

## Configuration

### Environment Variables
```
# /app/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://grkfoepzoqhloxanexmb.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
EMERGENT_LLM_KEY=sk-emergent-0614c65100c6d01374

# /app/backend/.env
SUPABASE_URL=https://grkfoepzoqhloxanexmb.supabase.co
SUPABASE_SERVICE_KEY=<service_role_key>
EMERGENT_LLM_KEY=sk-emergent-0614c65100c6d01374
```

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Basic chatbot UI
- [x] LLM integration
- [x] Supabase data fetching

### P1 (High Priority)
- [ ] Conversation history persistence (database)
- [ ] User authentication integration
- [ ] Role-based responses

### P2 (Medium Priority)
- [ ] Voice input support
- [ ] Export chat transcripts
- [ ] Analytics on chat usage

## Next Tasks
1. Add chat history persistence to Supabase
2. Integrate with existing auth system
3. Add more contextual data (user role, recent actions)
4. Implement suggested actions (quick buttons)
