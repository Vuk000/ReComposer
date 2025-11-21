#!/usr/bin/env python3
"""
Full authentication flow test.
"""

import asyncio
import httpx

async def test_auth_flow():
    """Test complete authentication flow."""
    print("=" * 70)
    print("Full Authentication Flow Test")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        # 1. Signup
        print("\n1. Testing Signup...")
        signup_response = await client.post(
            "http://localhost:8000/auth/signup",
            json={"email": "user1@example.com", "password": "password123"},
            timeout=10.0
        )
        print(f"   Status: {signup_response.status_code}")
        if signup_response.status_code == 201:
            signup_data = signup_response.json()
            token = signup_data['access_token']
            print(f"   ✅ Signup successful! Token: {token[:50]}...")
        else:
            print(f"   ❌ Signup failed: {signup_response.text}")
            return
        
        # 2. Get user info with token
        print("\n2. Testing /auth/me with token...")
        me_response = await client.get(
            "http://localhost:8000/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0
        )
        print(f"   Status: {me_response.status_code}")
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"   ✅ User info retrieved!")
            print(f"      Email: {me_data.get('email')}")
            print(f"      ID: {me_data.get('id')}")
        else:
            print(f"   ❌ /me failed: {me_response.text}")
        
        # 3. Login with same credentials
        print("\n3. Testing Login...")
        login_response = await client.post(
            "http://localhost:8000/auth/login",
            data={"username": "user1@example.com", "password": "password123"},
            timeout=10.0
        )
        print(f"   Status: {login_response.status_code}")
        if login_response.status_code == 200:
            login_data = login_response.json()
            new_token = login_data['access_token']
            print(f"   ✅ Login successful! Token: {new_token[:50]}...")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
        
        # 4. Try signup with existing email (should fail)
        print("\n4. Testing duplicate signup...")
        dup_response = await client.post(
            "http://localhost:8000/auth/signup",
            json={"email": "user1@example.com", "password": "password456"},
            timeout=10.0
        )
        print(f"   Status: {dup_response.status_code}")
        if dup_response.status_code == 400:
            print(f"   ✅ Correctly rejected duplicate email")
        else:
            print(f"   ⚠️  Expected 400, got {dup_response.status_code}: {dup_response.text}")
    
    print("\n" + "=" * 70)
    print("✅ Authentication Flow Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_auth_flow())

