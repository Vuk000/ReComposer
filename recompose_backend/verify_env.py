#!/usr/bin/env python3
"""
Verify that all required environment variables are set correctly.
"""

import os
import sys
from app.config import settings

def check_env_var(name: str, value: str, required: bool = True) -> tuple[bool, str]:
    """Check if an environment variable is set and valid."""
    if not value or value.strip() == "":
        if required:
            return False, f"❌ {name} is not set (REQUIRED)"
        else:
            return True, f"⚠️  {name} is not set (optional)"
    
    # Mask sensitive values for display
    if "key" in name.lower() or "secret" in name.lower() or "password" in name.lower():
        display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
    else:
        display_value = value
    
    return True, f"✅ {name} is set: {display_value}"

def main():
    """Verify all environment variables."""
    print("=" * 70)
    print("ReCompose AI - Environment Variable Verification")
    print("=" * 70)
    print()
    
    all_ok = True
    issues = []
    
    # Required variables
    checks = [
        ("DATABASE_URL", settings.DATABASE_URL, True),
        ("JWT_SECRET", settings.JWT_SECRET, True),
        ("ENCRYPTION_KEY", settings.ENCRYPTION_KEY, True),
        ("CELERY_BROKER_URL", settings.CELERY_BROKER_URL, True),
        ("CELERY_RESULT_BACKEND", settings.CELERY_RESULT_BACKEND, True),
    ]
    
    # AI Provider (at least one required)
    has_ai = bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)
    if not has_ai:
        all_ok = False
        issues.append("❌ No AI provider configured (OPENAI_API_KEY or ANTHROPIC_API_KEY required)")
    else:
        if settings.OPENAI_API_KEY:
            ok, msg = check_env_var("OPENAI_API_KEY", settings.OPENAI_API_KEY, False)
            print(msg)
        if settings.ANTHROPIC_API_KEY:
            ok, msg = check_env_var("ANTHROPIC_API_KEY", settings.ANTHROPIC_API_KEY, False)
            print(msg)
    
    # Brevo (required for email campaigns)
    has_brevo = bool(settings.BREVO_API_KEY and settings.BREVO_SMTP_USERNAME and settings.BREVO_SMTP_PASSWORD)
    if not has_brevo:
        issues.append("⚠️  Brevo not fully configured (required for email campaigns)")
    else:
        ok, msg = check_env_var("BREVO_API_KEY", settings.BREVO_API_KEY, False)
        print(msg)
        ok, msg = check_env_var("BREVO_SMTP_USERNAME", settings.BREVO_SMTP_USERNAME, False)
        print(msg)
        ok, msg = check_env_var("BREVO_SMTP_PASSWORD", settings.BREVO_SMTP_PASSWORD, False)
        print(msg)
    
    # Stripe (optional)
    has_stripe = bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLISHABLE_KEY)
    if has_stripe:
        ok, msg = check_env_var("STRIPE_SECRET_KEY", settings.STRIPE_SECRET_KEY, False)
        print(msg)
        ok, msg = check_env_var("STRIPE_PUBLISHABLE_KEY", settings.STRIPE_PUBLISHABLE_KEY, False)
        print(msg)
    
    # Check required variables
    for name, value, required in checks:
        ok, msg = check_env_var(name, value, required)
        print(msg)
        if not ok:
            all_ok = False
            issues.append(msg)
    
    # Validate JWT_SECRET length
    if settings.JWT_SECRET and len(settings.JWT_SECRET) < 32:
        all_ok = False
        issues.append(f"❌ JWT_SECRET is too short ({len(settings.JWT_SECRET)} chars, need 32+)")
    
    # Validate DATABASE_URL format
    if settings.DATABASE_URL and "asyncpg" not in settings.DATABASE_URL:
        issues.append("⚠️  DATABASE_URL should use asyncpg driver: postgresql+asyncpg://...")
    
    # Validate Redis URL format
    if settings.CELERY_BROKER_URL and not settings.CELERY_BROKER_URL.startswith("redis://"):
        all_ok = False
        issues.append("❌ CELERY_BROKER_URL should start with redis://")
    
    print()
    print("=" * 70)
    
    if all_ok and not issues:
        print("✅ All required environment variables are configured correctly!")
        print()
        print("Next steps:")
        print("1. Run: alembic upgrade head")
        print("2. Start backend: uvicorn app.main:app --reload")
        print("3. Start Celery worker: celery -A app.celery_app worker --loglevel=info")
        return 0
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

