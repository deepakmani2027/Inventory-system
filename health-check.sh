#!/bin/bash

# InventoryPro - Quick Health Check
# Run this to verify your setup is correct

echo "🏥 InventoryPro Health Check"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

failed=0

echo "Checking Backend..."
echo ""

# Check venv exists
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✅ Python venv found${NC}"
else
    echo -e "${RED}❌ Python venv not found${NC}"
    echo "   Run: python3 -m venv backend/venv"
    failed=$((failed+1))
fi

# Check requirements installed
if [ -d "backend/venv" ]; then
    if backend/venv/bin/python -c "import httpx" 2>/dev/null; then
        echo -e "${GREEN}✅ httpx installed${NC}"
    else
        echo -e "${RED}❌ httpx not installed${NC}"
        echo "   Run: backend/venv/bin/pip install httpx"
        failed=$((failed+1))
    fi

    if backend/venv/bin/python -c "import fastapi" 2>/dev/null; then
        echo -e "${GREEN}✅ fastapi installed${NC}"
    else
        echo -e "${RED}❌ fastapi not installed${NC}"
        echo "   Run: backend/venv/bin/pip install -r backend/requirements.txt"
        failed=$((failed+1))
    fi
fi

echo ""
echo "Checking Configuration..."
echo ""

# Check backend .env
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✅ backend/.env exists${NC}"

    if grep -q "OPENROUTER_API_KEY=sk-or-v1-" backend/.env; then
        echo -e "${GREEN}✅ OPENROUTER_API_KEY configured${NC}"
    elif grep -q "OPENROUTER_API_KEY=" backend/.env; then
        echo -e "${YELLOW}⚠️  OPENROUTER_API_KEY set but may be placeholder${NC}"
    else
        echo -e "${RED}❌ OPENROUTER_API_KEY not set${NC}"
        failed=$((failed+1))
    fi
else
    echo -e "${RED}❌ backend/.env not found${NC}"
    failed=$((failed+1))
fi

# Check frontend .env.local
if [ -f ".env.local" ]; then
    echo -e "${GREEN}✅ .env.local exists${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local not found (frontend may not work)${NC}"
fi

echo ""
echo "Checking Frontend..."
echo ""

# Check node_modules
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ node_modules installed${NC}"
else
    echo -e "${RED}❌ node_modules not found${NC}"
    echo "   Run: npm install"
    failed=$((failed+1))
fi

echo ""
echo "Runtime Checks..."
echo ""

# Test backend health (if running)
if command -v curl &> /dev/null; then
    response=$(curl -s -w "\n%{http_code}" http://localhost:8001/api/health 2>/dev/null | tail -n1)
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ Backend running on :8001${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend not responding (may not be started)${NC}"
        echo "   Start it with: bash start_backend.sh"
    fi
else
    echo -e "${YELLOW}⚠️  curl not found, skipping backend check${NC}"
fi

echo ""
echo "================================"
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "You're ready to run:"
    echo "  Terminal 1: bash start_backend.sh"
    echo "  Terminal 2: npm run dev"
else
    echo -e "${RED}❌ $failed check(s) failed${NC}"
    echo ""
    echo "See errors above and run the suggested fixes"
fi
