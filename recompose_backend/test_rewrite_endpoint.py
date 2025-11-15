#!/usr/bin/env python3
"""Test rewrite endpoint with OpenAI integration."""

import asyncio
import httpx

async def test_rewrite():
    """Test rewrite endpoint."""
    async with httpx.AsyncClient() as client:
        # First, signup and login
        print("1. Signing up...")
        signup_response = await client.post(
            "http://localhost:8000/auth/signup",
            json={
                "email": "rewritetest@example.com",
                "password": "TestPassword123"
            }
        )
        if signup_response.status_code != 201:
            print(f"   Signup failed: {signup_response.text}")
            return
        
        print("2. Logging in...")
        login_response = await client.post(
            "http://localhost:8000/auth/login",
            json={
                "email": "rewritetest@example.com",
                "password": "TestPassword123"
            }
        )
        if login_response.status_code != 200:
            print(f"   Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test rewrite endpoint
        print("3. Testing rewrite endpoint...")
        rewrite_response = await client.post(
            "http://localhost:8000/api/rewrite",
            json={
                "email_text": "Hey, I need this done ASAP!",
                "tone": "professional"
            },
            headers=headers
        )
        
        print(f"   Status: {rewrite_response.status_code}")
        if rewrite_response.status_code == 200:
            result = rewrite_response.json()
            print(f"   ✓ Rewrite successful!")
            print(f"   Rewritten: {result.get('rewritten_email', 'N/A')[:100]}...")
        else:
            print(f"   ✗ Rewrite failed: {rewrite_response.text}")
        
        # Test usage stats
        print("4. Testing usage stats...")
        usage_response = await client.get(
            "http://localhost:8000/api/rewrite/usage",
            headers=headers
        )
        if usage_response.status_code == 200:
            usage = usage_response.json()
            print(f"   ✓ Usage: {usage.get('used')}/{usage.get('limit')}")
        else:
            print(f"   ✗ Usage stats failed: {usage_response.text}")

if __name__ == "__main__":
    asyncio.run(test_rewrite())

