"""
Test script to verify all connections and API integrations.
This will show what's working and what needs real API keys.
"""

import asyncio
import sys
from app.config import settings
from app.db import engine
from sqlalchemy import text

async def test_database():
    """Test database connection."""
    print("\n🗄️  Testing Database Connection...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("   ✅ Database connected successfully")
            print(f"   📊 Database URL: {settings.DATABASE_URL}")
            return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_openai_config():
    """Test OpenAI configuration."""
    print("\n🤖 Testing OpenAI Configuration...")
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-your-openai-api-key-here":
        print("   ❌ OPENAI_API_KEY is not configured (placeholder value)")
        print("   ℹ️  AI rewriting features will NOT work")
        return False
    else:
        print(f"   ✅ OPENAI_API_KEY is configured: {settings.OPENAI_API_KEY[:20]}...")
        print(f"   📝 Model: {settings.OPENAI_MODEL}")
        return True

def test_anthropic_config():
    """Test Anthropic configuration."""
    print("\n🤖 Testing Anthropic Configuration...")
    if not settings.ANTHROPIC_API_KEY:
        print("   ⚠️  ANTHROPIC_API_KEY is not configured")
        print("   ℹ️  Using OpenAI as AI provider (if configured)")
        return False
    else:
        print(f"   ✅ ANTHROPIC_API_KEY is configured: {settings.ANTHROPIC_API_KEY[:20]}...")
        print(f"   📝 Model: {settings.ANTHROPIC_MODEL}")
        print(f"   🔧 USE_ANTHROPIC: {settings.USE_ANTHROPIC}")
        return True

def test_stripe_config():
    """Test Stripe configuration."""
    print("\n💳 Testing Stripe Configuration...")
    if not settings.STRIPE_SECRET_KEY:
        print("   ❌ STRIPE_SECRET_KEY is not configured")
        print("   ℹ️  Billing features are DISABLED")
        print(f"   🔧 BILLING_ENABLED: {settings.BILLING_ENABLED}")
        return False
    else:
        print(f"   ✅ STRIPE_SECRET_KEY is configured: {settings.STRIPE_SECRET_KEY[:20]}...")
        print(f"   🔧 BILLING_ENABLED: {settings.BILLING_ENABLED}")
        return True

def test_brevo_config():
    """Test Brevo email configuration."""
    print("\n📧 Testing Brevo Email Configuration...")
    has_api_key = bool(settings.BREVO_API_KEY)
    has_smtp_user = bool(settings.BREVO_SMTP_USERNAME)
    has_smtp_pass = bool(settings.BREVO_SMTP_PASSWORD)
    
    if not has_api_key:
        print("   ❌ BREVO_API_KEY is not configured")
    else:
        print(f"   ✅ BREVO_API_KEY is configured: {settings.BREVO_API_KEY[:20]}...")
    
    if not has_smtp_user:
        print("   ❌ BREVO_SMTP_USERNAME is not configured")
    else:
        print(f"   ✅ BREVO_SMTP_USERNAME is configured: {settings.BREVO_SMTP_USERNAME}")
    
    if not has_smtp_pass:
        print("   ❌ BREVO_SMTP_PASSWORD is not configured")
    else:
        print(f"   ✅ BREVO_SMTP_PASSWORD is configured")
    
    if not (has_api_key and has_smtp_user and has_smtp_pass):
        print("   ℹ️  Email campaign features will NOT work")
        return False
    
    print(f"   📨 SMTP Server: {settings.BREVO_SMTP_SERVER}:{settings.BREVO_SMTP_PORT}")
    return True

def test_security_config():
    """Test security configuration."""
    print("\n🔐 Testing Security Configuration...")
    
    # JWT Secret
    if settings.JWT_SECRET == "your-secret-key-change-in-production":
        print("   ⚠️  JWT_SECRET is using DEFAULT value (INSECURE!)")
        print("   🚨 WARNING: JWT tokens can be forged!")
    else:
        print(f"   ✅ JWT_SECRET is configured (length: {len(settings.JWT_SECRET)} characters)")
    
    # Encryption Key
    if not settings.ENCRYPTION_KEY:
        print("   ❌ ENCRYPTION_KEY is not configured")
        print("   ℹ️  OAuth token encryption will NOT work")
        return False
    else:
        print(f"   ✅ ENCRYPTION_KEY is configured")
        return True

def test_cors_config():
    """Test CORS configuration."""
    print("\n🌐 Testing CORS Configuration...")
    origins = settings.CORS_ORIGINS
    print(f"   ✅ CORS Origins configured: {origins}")
    return True

async def main():
    """Run all tests."""
    print("=" * 60)
    print("🔍 ReCompose AI - Connection & Integration Test")
    print("=" * 60)
    
    results = {}
    
    # Run all tests
    results['database'] = await test_database()
    results['openai'] = test_openai_config()
    results['anthropic'] = test_anthropic_config()
    results['stripe'] = test_stripe_config()
    results['brevo'] = test_brevo_config()
    results['security'] = test_security_config()
    results['cors'] = test_cors_config()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    print("\n🔧 Required Actions:")
    
    if not results['openai'] and not results['anthropic']:
        print("   1. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env file")
        print("      → Get OpenAI key: https://platform.openai.com/api-keys")
        print("      → Get Anthropic key: https://console.anthropic.com/")
    
    if not results['stripe']:
        print("   2. Add STRIPE_SECRET_KEY to .env file (if billing needed)")
        print("      → Get Stripe keys: https://dashboard.stripe.com/test/apikeys")
    
    if not results['brevo']:
        print("   3. Add BREVO credentials to .env file (if email campaigns needed)")
        print("      → Get Brevo API key: https://app.brevo.com/settings/keys/api")
    
    if not results['security']:
        print("   4. Add ENCRYPTION_KEY to .env file")
        print("      → Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
    
    print("\n💡 What's Working NOW:")
    if results['database']:
        print("   ✅ User authentication (signup/login)")
        print("   ✅ Database operations")
        print("   ✅ API endpoints (/docs)")
    
    print("\n❌ What's NOT Working (needs API keys):")
    if not results['openai'] and not results['anthropic']:
        print("   ❌ AI email rewriting")
    if not results['stripe']:
        print("   ❌ Billing/subscriptions")
    if not results['brevo']:
        print("   ❌ Email campaigns")
    
    print("\n" + "=" * 60)
    print(f"🌐 Backend Server: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if passed >= 3 else 1)

if __name__ == "__main__":
    asyncio.run(main())

