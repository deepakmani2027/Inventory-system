#!/usr/bin/env python3
"""
InventoryPro Chatbot Backend API Testing
Tests the FastAPI backend endpoints for the chatbot functionality
"""

import requests
import json
import sys
from datetime import datetime
import time

class ChatbotAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_keys = ["status", "service"]
                has_keys = all(key in data for key in expected_keys)
                success = has_keys and data["status"] == "healthy"
                details = f"Response: {data}" if success else f"Missing keys or wrong status: {data}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Health Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("Health Endpoint", False, str(e))
            return False

    def test_chat_endpoint_basic(self):
        """Test basic chat functionality"""
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello, what can you help me with?"}
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_keys = ["message", "sessionId"]
                has_keys = all(key in data for key in required_keys)
                has_content = len(data.get("message", "")) > 0
                success = has_keys and has_content
                
                if success:
                    self.session_id = data["sessionId"]
                    details = f"Got response: {data['message'][:100]}..."
                else:
                    details = f"Missing keys or empty message: {data}"
            else:
                details = f"Status code: {response.status_code}, Response: {response.text}"
                
            self.log_test("Basic Chat Request", success, details)
            return success
            
        except Exception as e:
            self.log_test("Basic Chat Request", False, str(e))
            return False

    def test_inventory_questions(self):
        """Test inventory-specific questions"""
        inventory_questions = [
            "What items are in stock?",
            "Show me low stock alerts",
            "What are the recent sales?",
            "How do I create a bill?"
        ]
        
        success_count = 0
        
        for question in inventory_questions:
            try:
                payload = {
                    "messages": [
                        {"role": "user", "content": question}
                    ],
                    "sessionId": self.session_id
                }
                
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("message") and len(data["message"]) > 10:
                        success_count += 1
                        print(f"   ✅ '{question}' - Got response: {data['message'][:80]}...")
                    else:
                        print(f"   ❌ '{question}' - Empty or short response")
                else:
                    print(f"   ❌ '{question}' - Status: {response.status_code}")
                    
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ '{question}' - Error: {str(e)}")
        
        success = success_count == len(inventory_questions)
        self.log_test(f"Inventory Questions ({success_count}/{len(inventory_questions)})", success)
        return success

    def test_conversation_context(self):
        """Test that the chatbot maintains conversation context"""
        try:
            # First message
            payload1 = {
                "messages": [
                    {"role": "user", "content": "What's the current stock level?"}
                ],
                "sessionId": self.session_id
            }
            
            response1 = requests.post(
                f"{self.base_url}/api/chat",
                json=payload1,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response1.status_code != 200:
                self.log_test("Conversation Context", False, f"First request failed: {response1.status_code}")
                return False
            
            data1 = response1.json()
            session_id = data1.get("sessionId", self.session_id)
            
            # Follow-up message that requires context
            payload2 = {
                "messages": [
                    {"role": "user", "content": "What's the current stock level?"},
                    {"role": "assistant", "content": data1["message"]},
                    {"role": "user", "content": "Can you tell me more about the low stock items?"}
                ],
                "sessionId": session_id
            }
            
            response2 = requests.post(
                f"{self.base_url}/api/chat",
                json=payload2,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response2.status_code == 200
            if success:
                data2 = response2.json()
                has_response = len(data2.get("message", "")) > 10
                success = has_response
                details = f"Context maintained, got response: {data2['message'][:80]}..." if success else "No meaningful response"
            else:
                details = f"Status code: {response2.status_code}"
                
            self.log_test("Conversation Context", success, details)
            return success
            
        except Exception as e:
            self.log_test("Conversation Context", False, str(e))
            return False

    def test_supabase_integration(self):
        """Test that the chatbot can access Supabase data"""
        try:
            # Ask for specific inventory data that should come from Supabase
            payload = {
                "messages": [
                    {"role": "user", "content": "Show me the exact inventory quantities for all items"}
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                message = data.get("message", "").lower()
                
                # Check if response contains inventory-related terms
                inventory_indicators = ["stock", "quantity", "inventory", "items", "warehouse", "units"]
                has_inventory_data = any(indicator in message for indicator in inventory_indicators)
                
                # Check if it's not just a generic response
                generic_responses = ["i don't have", "unable to", "cannot access", "no data"]
                is_generic = any(generic in message for generic in generic_responses)
                
                success = has_inventory_data and not is_generic
                details = f"Response contains inventory data: {data['message'][:100]}..." if success else f"Generic or no inventory data: {message[:100]}..."
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Supabase Integration", success, details)
            return success
            
        except Exception as e:
            self.log_test("Supabase Integration", False, str(e))
            return False

    def test_error_handling(self):
        """Test error handling with malformed requests"""
        test_cases = [
            {
                "name": "Empty messages",
                "payload": {"messages": []},
                "expect_error": True
            },
            {
                "name": "Invalid message format",
                "payload": {"messages": [{"invalid": "format"}]},
                "expect_error": True
            },
            {
                "name": "Missing messages field",
                "payload": {"sessionId": "test"},
                "expect_error": True
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=test_case["payload"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if test_case["expect_error"]:
                    # Should return error status
                    if response.status_code >= 400:
                        success_count += 1
                        print(f"   ✅ {test_case['name']} - Correctly returned error: {response.status_code}")
                    else:
                        print(f"   ❌ {test_case['name']} - Should have returned error but got: {response.status_code}")
                else:
                    # Should return success
                    if response.status_code == 200:
                        success_count += 1
                        print(f"   ✅ {test_case['name']} - Success")
                    else:
                        print(f"   ❌ {test_case['name']} - Expected success but got: {response.status_code}")
                        
            except Exception as e:
                print(f"   ❌ {test_case['name']} - Exception: {str(e)}")
        
        success = success_count == len(test_cases)
        self.log_test(f"Error Handling ({success_count}/{len(test_cases)})", success)
        return success

    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🚀 Starting InventoryPro Chatbot Backend Tests")
        print("=" * 60)
        
        # Test health endpoint first
        if not self.test_health_endpoint():
            print("❌ Health check failed - stopping tests")
            return False
        
        # Test basic chat functionality
        if not self.test_chat_endpoint_basic():
            print("❌ Basic chat failed - stopping tests")
            return False
        
        # Test inventory-specific questions
        self.test_inventory_questions()
        
        # Test conversation context
        self.test_conversation_context()
        
        # Test Supabase integration
        self.test_supabase_integration()
        
        # Test error handling
        self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test runner"""
    tester = ChatbotAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())