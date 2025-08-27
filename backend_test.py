#!/usr/bin/env python3
"""
Backend API Testing Suite for Typing Practice Website
Tests all backend endpoints according to test_result.md requirements
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend env (as per system requirements)
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")

API_BASE = f"{BACKEND_URL}/api"

print(f"Testing backend API at: {API_BASE}")

def test_root_endpoint():
    """Test GET /api/ should return {message: 'Hello World'}"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                print("✅ Root endpoint test PASSED")
                return True
            else:
                print(f"❌ Root endpoint test FAILED: Expected message 'Hello World', got {data}")
                return False
        else:
            print(f"❌ Root endpoint test FAILED: Expected status 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint test FAILED with exception: {e}")
        return False

def test_create_session_valid():
    """Test POST /api/sessions with valid data"""
    print("\n=== Testing Create Session (Valid Data) ===")
    
    # Use realistic test data
    test_session = {
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "mode": "time",
        "duration_seconds": 60,
        "words_count": 45,
        "wpm": 75.5,
        "accuracy": 96.2,
        "consistency": 88.7,
        "started_at": "2024-01-15T10:30:00Z",
        "ended_at": "2024-01-15T10:31:00Z",
        "raw_typed": "the quick brown fox jumps over the lazy dog",
        "target_text": "the quick brown fox jumps over the lazy dog"
    }
    
    try:
        response = requests.post(f"{API_BASE}/sessions", json=test_session)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            # Check required fields
            if "id" in data and "created_at" in data:
                # Verify UUID format
                try:
                    uuid.UUID(data["id"])
                    print("✅ Session ID is valid UUID")
                except ValueError:
                    print(f"❌ Session ID is not valid UUID: {data['id']}")
                    return False
                
                # Verify created_at is ISO string
                try:
                    datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                    print("✅ created_at is valid ISO datetime string")
                except ValueError:
                    print(f"❌ created_at is not valid ISO datetime: {data['created_at']}")
                    return False
                
                print("✅ Create session test PASSED")
                return True, data
            else:
                print(f"❌ Create session test FAILED: Missing id or created_at in response")
                return False, None
        else:
            print(f"❌ Create session test FAILED: Expected status 200, got {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Create session test FAILED with exception: {e}")
        return False, None

def test_create_session_invalid():
    """Test POST /api/sessions with negative wpm/accuracy should return 400"""
    print("\n=== Testing Create Session (Invalid Data - Negative Values) ===")
    
    # Test negative WPM
    test_session_negative_wpm = {
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "mode": "time",
        "duration_seconds": 60,
        "words_count": 45,
        "wpm": -10.5,  # Negative WPM
        "accuracy": 96.2,
        "consistency": 88.7
    }
    
    try:
        response = requests.post(f"{API_BASE}/sessions", json=test_session_negative_wpm)
        print(f"Negative WPM - Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Negative WPM validation test PASSED")
            negative_wpm_passed = True
        else:
            print(f"❌ Negative WPM validation test FAILED: Expected status 400, got {response.status_code}")
            negative_wpm_passed = False
    except Exception as e:
        print(f"❌ Negative WPM validation test FAILED with exception: {e}")
        negative_wmp_passed = False
    
    # Test negative accuracy
    test_session_negative_accuracy = {
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "mode": "time",
        "duration_seconds": 60,
        "words_count": 45,
        "wpm": 75.5,
        "accuracy": -5.2,  # Negative accuracy
        "consistency": 88.7
    }
    
    try:
        response = requests.post(f"{API_BASE}/sessions", json=test_session_negative_accuracy)
        print(f"Negative Accuracy - Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Negative accuracy validation test PASSED")
            negative_accuracy_passed = True
        else:
            print(f"❌ Negative accuracy validation test FAILED: Expected status 400, got {response.status_code}")
            negative_accuracy_passed = False
    except Exception as e:
        print(f"❌ Negative accuracy validation test FAILED with exception: {e}")
        negative_accuracy_passed = False
    
    return negative_wpm_passed and negative_accuracy_passed

def test_list_sessions(test_user_id=None):
    """Test GET /api/sessions and GET /api/sessions?user_id=..."""
    print("\n=== Testing List Sessions ===")
    
    try:
        # Test without filter
        response = requests.get(f"{API_BASE}/sessions")
        print(f"All sessions - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"All sessions count: {len(data)}")
            print("✅ List all sessions test PASSED")
            all_sessions_passed = True
        else:
            print(f"❌ List all sessions test FAILED: Expected status 200, got {response.status_code}")
            all_sessions_passed = False
        
        # Test with user_id filter if provided
        if test_user_id:
            response_filtered = requests.get(f"{API_BASE}/sessions", params={"user_id": test_user_id})
            print(f"Filtered sessions - Status Code: {response_filtered.status_code}")
            
            if response_filtered.status_code == 200:
                filtered_data = response_filtered.json()
                print(f"Filtered sessions count: {len(filtered_data)}")
                
                # Verify all returned sessions have the correct user_id
                if all(session.get("user_id") == test_user_id for session in filtered_data):
                    print("✅ List sessions with user_id filter test PASSED")
                    filtered_sessions_passed = True
                else:
                    print("❌ List sessions with user_id filter test FAILED: Some sessions have wrong user_id")
                    filtered_sessions_passed = False
            else:
                print(f"❌ List sessions with user_id filter test FAILED: Expected status 200, got {response_filtered.status_code}")
                filtered_sessions_passed = False
        else:
            filtered_sessions_passed = True  # Skip if no test user provided
        
        return all_sessions_passed and filtered_sessions_passed
        
    except Exception as e:
        print(f"❌ List sessions test FAILED with exception: {e}")
        return False

def test_leaderboard():
    """Test GET /api/leaderboard returns list sorted by wpm desc"""
    print("\n=== Testing Leaderboard ===")
    
    try:
        response = requests.get(f"{API_BASE}/leaderboard")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Leaderboard entries count: {len(data)}")
            
            if len(data) > 1:
                # Check if sorted by wpm descending
                wpms = [entry.get("wpm", 0) for entry in data]
                is_sorted_desc = all(wpms[i] >= wpms[i+1] for i in range(len(wpms)-1))
                
                if is_sorted_desc:
                    print("✅ Leaderboard sorting test PASSED")
                    sorting_passed = True
                else:
                    print(f"❌ Leaderboard sorting test FAILED: WPMs not sorted descending: {wpms}")
                    sorting_passed = False
            else:
                print("✅ Leaderboard test PASSED (insufficient data to test sorting)")
                sorting_passed = True
            
            # Verify required fields in response
            if data:
                first_entry = data[0]
                required_fields = ["user_id", "wpm", "accuracy", "mode"]
                missing_fields = [field for field in required_fields if field not in first_entry]
                
                if not missing_fields:
                    print("✅ Leaderboard response format test PASSED")
                    format_passed = True
                else:
                    print(f"❌ Leaderboard response format test FAILED: Missing fields {missing_fields}")
                    format_passed = False
            else:
                print("✅ Leaderboard response format test PASSED (empty leaderboard)")
                format_passed = True
            
            return sorting_passed and format_passed
        else:
            print(f"❌ Leaderboard test FAILED: Expected status 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Leaderboard test FAILED with exception: {e}")
        return False

def run_all_tests():
    """Run all backend API tests"""
    print("🚀 Starting Backend API Tests")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Root endpoint
    results["root_endpoint"] = test_root_endpoint()
    
    # Test 2: Create session with valid data
    create_result, created_session = test_create_session_valid()
    results["create_session_valid"] = create_result
    
    # Test 3: Create session with invalid data
    results["create_session_invalid"] = test_create_session_invalid()
    
    # Test 4: List sessions (with and without filter)
    test_user_id = created_session.get("user_id") if created_session else None
    results["list_sessions"] = test_list_sessions(test_user_id)
    
    # Test 5: Leaderboard
    results["leaderboard"] = test_leaderboard()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All backend tests PASSED!")
        return True
    else:
        print("⚠️  Some backend tests FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)