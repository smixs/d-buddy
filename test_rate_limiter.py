#!/usr/bin/env python3
"""
Simple test script for RateLimiterService
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.rate_limiter import RateLimiterService

def test_rate_limiter():
    """Test the rate limiter functionality"""
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize rate limiter with test directory
        rate_limiter = RateLimiterService(data_dir=temp_dir, max_requests_per_hour=3)
        
        print("🧪 Testing Rate Limiter...")
        
        # Test 1: Admin user should have unlimited access
        print("\n1. Testing admin user (ultrathink):")
        for i in range(5):
            can_make = rate_limiter.can_make_request("123", "ultrathink")
            print(f"   Request {i+1}: {can_make}")
            if can_make:
                rate_limiter.record_request("123", "ultrathink")
        
        # Test 2: Regular user should be limited to 3 requests
        print("\n2. Testing regular user:")
        user_id = "456"
        username = "testuser"
        
        for i in range(5):
            can_make = rate_limiter.can_make_request(user_id, username)
            remaining = rate_limiter.get_remaining_requests(user_id, username)
            print(f"   Request {i+1}: can_make={can_make}, remaining={remaining}")
            
            if can_make:
                rate_limiter.record_request(user_id, username)
            else:
                wait_time = rate_limiter.get_time_until_next_request(user_id, username)
                print(f"   Need to wait: {wait_time}")
        
        # Test 3: Case-insensitive admin check
        print("\n3. Testing case-insensitive admin check:")
        admin_usernames = ["ultrathink", "ULTRATHINK", "UltraThink"]
        for admin_name in admin_usernames:
            is_admin = rate_limiter.is_admin(admin_name)
            print(f"   '{admin_name}' is admin: {is_admin}")
        
        print("\n✅ Rate limiter tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_rate_limiter()