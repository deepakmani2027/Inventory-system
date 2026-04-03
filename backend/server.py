from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import httpx

load_dotenv()

app = FastAPI(title="InventoryPro Chatbot API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://grkfoepzoqhloxanexmb.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdya2ZvZXB6b3FobG94YW5leG1iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NjI4MiwiZXhwIjoyMDkwMzMyMjgyfQ.95StP-il6HMseMVbMPsyEfCJKHcjwEysFCshKBoZ-s0")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("⚠️  WARNING: OPENROUTER_API_KEY not set in environment variables")
    print("Get your API key from: https://openrouter.ai/settings/keys")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# OpenRouter API Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    sessionId: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    sessionId: str

async def get_inventory_context() -> str:
    """Fetch current inventory data from Supabase"""
    try:
        # Fetch categories
        categories = supabase.table('categories').select('id, name, description').limit(50).execute()
        
        # Fetch items with category
        items = supabase.table('items').select('id, name, description, unit_price, reorder_level, category_id').limit(100).execute()
        
        # Fetch inventory
        inventory = supabase.table('inventory').select('quantity, warehouse_location, last_restocked, item_id').limit(100).execute()
        
        # Fetch recent sales
        sales = supabase.table('sales').select('id, bill_number, customer_name, total_amount, status, sale_date').order('sale_date', desc=True).limit(10).execute()
        
        # Build context
        context = "=== INVENTORYPRO DATABASE CONTEXT ===\n\n"
        
        # Categories
        context += "## Categories Available:\n"
        cat_map = {}
        for cat in categories.data or []:
            cat_map[cat['id']] = cat['name']
            context += f"- {cat['name']}: {cat.get('description', 'No description')}\n"
        
        # Items
        context += "\n## Items in Inventory:\n"
        item_map = {}
        for item in items.data or []:
            item_map[item['id']] = item
            cat_name = cat_map.get(item['category_id'], 'Unknown')
            context += f"- {item['name']} (Category: {cat_name}) - Price: ${item['unit_price']}, Reorder Level: {item['reorder_level']}\n"
        
        # Stock levels
        context += "\n## Current Stock Levels:\n"
        low_stock = []
        for inv in inventory.data or []:
            item = item_map.get(inv['item_id'], {})
            item_name = item.get('name', 'Unknown Item')
            context += f"- {item_name}: {inv['quantity']} units at {inv.get('warehouse_location', 'Unknown location')}\n"
            
            if inv['quantity'] <= item.get('reorder_level', 10):
                low_stock.append((item_name, inv['quantity'], item.get('reorder_level', 10)))
        
        # Low stock alerts
        if low_stock:
            context += "\n## LOW STOCK ALERTS:\n"
            for name, qty, reorder in low_stock:
                context += f"- {name}: Only {qty} left (reorder level: {reorder})\n"
        
        # Recent sales
        context += "\n## Recent Sales (Last 10):\n"
        for sale in sales.data or []:
            context += f"- {sale.get('bill_number', 'N/A')}: {sale.get('customer_name', 'Walk-in')} - ${sale['total_amount']} ({sale['status']})\n"
        
        return context
    except Exception as e:
        print(f"Error fetching inventory context: {e}")
        return "Unable to fetch inventory data at this time."

SYSTEM_PROMPT = """You are InventoryPro Assistant, an AI helper for the InventoryPro inventory management platform. You help users with:

1. **Inventory Questions**: Stock levels, item availability, warehouse locations
2. **Sales Information**: Recent transactions, bill details, revenue insights
3. **Platform Navigation**: How to use features like billing, restocking, returns
4. **Role Guidance**: Admin, Salesman, Inventory Manager, Sales Manager workflows

## Response Guidelines:
- Be concise and helpful
- Use the actual data when answering inventory/sales questions
- For actions (like creating bills), guide users to the appropriate dashboard section
- If you don't have specific data, say so clearly
- Format numbers nicely (e.g., "$999.99" for prices)
- Alert users about low stock items when relevant

## Platform Features:
- Dashboard: Analytics, revenue tracking, performance metrics
- Billing: Create bills, manage transactions
- Inventory: Restock items, track stock movements
- Returns: Process customer returns
- Settings: Manage users, categories, items"""

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "InventoryPro Chatbot"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that uses OpenRouter API for LLM inference.
    Docs: https://openrouter.ai/docs
    """
    try:
        # Validate API key
        if not OPENROUTER_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OPENROUTER_API_KEY not configured. Get it from: https://openrouter.ai/settings/keys"
            )

        # Get fresh inventory context
        inventory_context = await get_inventory_context()
        full_system = f"{SYSTEM_PROMPT}\n\n## Current Database State:\n{inventory_context}"

        # Generate session ID
        import uuid
        session_id = request.sessionId or str(uuid.uuid4())

        # Build conversation messages
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        # Call OpenRouter API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://inventorypro.local",
                    "X-OpenRouter-Title": "InventoryPro Chatbot",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": full_system},
                        *messages
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
                timeout=30.0
            )

            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ OpenRouter API Error: {response.status_code}")
                print(f"Response: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenRouter API error: {error_detail}"
                )

            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]

            return ChatResponse(
                message=assistant_message,
                sessionId=session_id
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="OpenRouter API request timed out. Please try again."
        )
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
