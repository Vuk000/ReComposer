#!/usr/bin/env python3
"""Test signup API endpoint with detailed error handling."""

import asyncio
import httpx

async def test_signup():
    """Test signup endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            # Test signup
            response = await client.post(
                "http://localhost:8000/auth/signup",
                json={
                    "email": "testapi@example.com",
                    "password": "TestPassword123"
                },
                timeout=10.0
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 201:
                print("✓ Signup successful!")
                data = response.json()
                print(f"  User ID: {data.get('id')}")
                print(f"  Email: {data.get('email')}")
            else:
                print("✗ Signup failed")
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data}")
                except:
                    print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_signup())

