import asyncio
import time
from typing import Dict, Any, Optional
import requests

class CacheTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """Login and get access token"""
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{self.base_url}/login", data=data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print(f"✅ Login successful for {username}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def get_notes(self, skip: int = 0, limit: int = 10, search: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get notes with timing"""
        if not self.token:
            print("❌ Not logged in")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"skip": str(skip), "limit": str(limit)}
        if search:
            params["search"] = search
        
        start_time = time.time()
        response = requests.get(f"{self.base_url}/notes/", headers=headers, params=params)
        end_time = time.time()
        
        return {
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "data": response.json() if response.status_code == 200 else response.text,
            "headers": dict(response.headers)
        }
    
    def create_note(self, text: str) -> Optional[Dict[str, Any]]:
        """Create a new note"""
        if not self.token:
            print("❌ Not logged in")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        data = {"text": text}
        
        response = requests.post(f"{self.base_url}/notes/", headers=headers, json=data)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else response.text
        }
    
    def delete_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Delete a note"""
        if not self.token:
            print("❌ Not logged in")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.delete(f"{self.base_url}/notes/{note_id}", headers=headers)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else response.text
        }

def test_caching():
    """Test the caching functionality"""
    tester = CacheTester()
    
    print("🚀 Starting cache testing...")
    
    # Login
    if not tester.login():
        return
    
    print("\n📋 Test 1: First GET request (should be cache MISS)")
    result1 = tester.get_notes()
    if result1:
        print(f"Status: {result1['status_code']}")
        print(f"Response time: {result1['response_time']:.3f}s")
        print(f"Notes count: {len(result1['data'])}")
    
    print("\n📋 Test 2: Second GET request (should be cache HIT)")
    result2 = tester.get_notes()
    if result2:
        print(f"Status: {result2['status_code']}")
        print(f"Response time: {result2['response_time']:.3f}s")
        print(f"Notes count: {len(result2['data'])}")
    
    # Check if second request was faster
    if result1 and result2:
        speedup = result1['response_time'] / result2['response_time']
        print(f"Speedup: {speedup:.2f}x faster")
    
    print("\n📝 Test 3: Create a new note (should invalidate cache)")
    create_result = tester.create_note("Test note for cache invalidation")
    if create_result:
        print(f"Status: {create_result['status_code']}")
        if create_result['status_code'] == 200:
            note_id = create_result['data']['id']
            print(f"Created note with ID: {note_id}")
    
    print("\n📋 Test 4: GET request after creating note (should be cache MISS again)")
    result3 = tester.get_notes()
    if result3:
        print(f"Status: {result3['status_code']}")
        print(f"Response time: {result3['response_time']:.3f}s")
        print(f"Notes count: {len(result3['data'])}")
    
    print("\n📋 Test 5: Second GET request after creating note (should be cache HIT)")
    result4 = tester.get_notes()
    if result4:
        print(f"Status: {result4['status_code']}")
        print(f"Response time: {result4['response_time']:.3f}s")
        print(f"Notes count: {len(result4['data'])}")
    
    # Clean up - delete the test note
    if create_result and create_result['status_code'] == 200:
        note_id = create_result['data']['id']
        print(f"\n🗑️ Cleaning up - deleting note {note_id}")
        delete_result = tester.delete_note(note_id)
        if delete_result:
            print(f"Delete status: {delete_result['status_code']}")
    
    print("\n✅ Cache testing completed!")

if __name__ == "__main__":
    test_caching() 