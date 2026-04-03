#!/bin/bash
set -e

echo "🚀 InventoryPro AI Chatbot - Complete Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Error: Must run from project root directory${NC}"
    echo "Run: cd /path/to/inventory-main && bash setup.sh"
    exit 1
fi

echo -e "${YELLOW}📦 Step 1: Installing Backend Dependencies${NC}"
cd backend

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing Python packages..."
pip install -q -r requirements.txt

if pip show httpx > /dev/null 2>&1; then
    echo -e "${GREEN}✅ httpx installed${NC}"
else
    echo -e "${YELLOW}Installing httpx...${NC}"
    pip install -q httpx
fi

echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ backend/.env file not found${NC}"
    echo -e "${YELLOW}Creating .env with placeholder values...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Edit backend/.env and set your OPENROUTER_API_KEY${NC}"
else
    if grep -q "OPENROUTER_API_KEY=.*your_" .env; then
        echo -e "${RED}⚠️  WARNING: OPENROUTER_API_KEY not set (still placeholder)${NC}"
        echo "Get your key from: https://openrouter.ai/settings/keys"
    else
        echo -e "${GREEN}✅ OPENROUTER_API_KEY is configured${NC}"
    fi
fi

cd ..

echo ""
echo -e "${YELLOW}📦 Step 2: Installing Frontend Dependencies${NC}"
if npm list > /dev/null 2>&1; then
    echo -e "${GREEN}✅ npm dependencies already installed${NC}"
else
    echo "Installing Node packages..."
    npm install -q
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo -e "${YELLOW}🚀 To start the servers:${NC}"
echo ""
echo -e "${GREEN}Terminal 1 - Backend:${NC}"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo -e "${GREEN}Terminal 2 - Frontend:${NC}"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Then visit: http://localhost:3000${NC}"
echo ""
