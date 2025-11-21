# Production Deployment Guide

This guide covers the essential steps for deploying ReCompose AI to production.

## 1. Generate Secure Keys

**CRITICAL:** Never use default keys in production!

### Generate JWT Secret and Encryption Key

Run the key generation script:

```bash
python generate_keys.py
```

This will output:
```
JWT_SECRET=<64-character-hex-string>
ENCRYPTION_KEY=<base64-encoded-fernet-key>
```

Copy these values to your `.env` file.

### Manual Generation (Alternative)

If you prefer to generate keys manually:

```bash
# Generate JWT Secret (64 hex characters = 32 bytes)
python -c "import secrets; print(secrets.token_hex(32))"

# Generate Encryption Key (Fernet key for OAuth tokens)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 2. Update Environment Variables

### Required for Production

Update these values in your `.env` file:

```env
# Security Keys (REQUIRED - use generate_keys.py)
JWT_SECRET=<generated-64-char-hex-string>
ENCRYPTION_KEY=<generated-fernet-key>

# Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/recompose

# AI Provider (REQUIRED - at least one)
OPENAI_API_KEY=sk-proj-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
USE_ANTHROPIC=true

# CORS Origins (REQUIRED - update for your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend/Backend URLs (REQUIRED)
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com

# Environment
DEBUG=false
ENVIRONMENT=production
LOG_FORMAT=json
```

### Optional (for full functionality)

```env
# Billing (if using Stripe)
BILLING_ENABLED=true
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email Campaigns (if using Brevo)
BREVO_API_KEY=xkeysib-...
BREVO_SMTP_USERNAME=your-email@domain.com
BREVO_SMTP_PASSWORD=your-smtp-key

# Redis (for Celery background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 3. CORS Configuration

Update `CORS_ORIGINS` in your `.env` file to include your production frontend domain(s):

```env
# Development (default)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Production (example)
CORS_ORIGINS=https://app.recompose.ai,https://www.recompose.ai
```

**Important:**
- Use HTTPS in production
- Include all domains that will access the API
- Separate multiple origins with commas (no spaces)
- Do NOT use wildcards (`*`) in production

## 4. Database Setup

### Run Migrations

```bash
alembic upgrade head
```

### Verify Tables

```bash
python check_tables.py
```

## 5. Security Checklist

- [ ] JWT_SECRET is 64+ characters (generated, not default)
- [ ] ENCRYPTION_KEY is set (for OAuth token encryption)
- [ ] DEBUG=false in production
- [ ] LOG_FORMAT=json for structured logging
- [ ] CORS_ORIGINS includes only your production domains
- [ ] Database uses strong password
- [ ] API keys are real (not placeholders)
- [ ] HTTPS is enabled (via reverse proxy/load balancer)
- [ ] Environment variables are not committed to version control

## 6. Start Services

### Backend API Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or with production ASGI server (recommended):

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Celery Worker (for background tasks)

```bash
celery -A app.celery_app worker --loglevel=info
```

### Celery Beat (for scheduled tasks)

```bash
celery -A app.celery_app beat --loglevel=info
```

## 7. Health Check

Verify the API is running:

```bash
curl https://api.yourdomain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## 8. Frontend Configuration

Update frontend environment variables:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

Build the frontend:

```bash
cd frontend-react
npm run build
```

Deploy the `dist/` folder to your hosting provider.

## 9. Monitoring

### Logs

With `LOG_FORMAT=json`, logs are structured JSON for easy parsing:

```json
{
  "timestamp": "2025-01-01T00:00:00Z",
  "level": "INFO",
  "logger": "app.main",
  "message": "POST /api/auth/login",
  "request_id": "abc123"
}
```

### Health Monitoring

Set up monitoring to check `/health` endpoint regularly.

### Error Tracking

Consider integrating:
- Sentry for error tracking
- DataDog/New Relic for APM
- CloudWatch/Loggly for log aggregation

## 10. SSL/TLS

Ensure HTTPS is configured:

1. **Reverse Proxy (Recommended):**
   - Use Nginx or Caddy as reverse proxy
   - Handle SSL termination at proxy level
   - Forward to backend on localhost:8000

2. **Load Balancer:**
   - AWS ALB, GCP Load Balancer, etc.
   - Handle SSL at load balancer level

3. **Application Level:**
   - Not recommended for production
   - Use reverse proxy instead

## Troubleshooting

### JWT Secret Warning

If you see: `JWT_SECRET should be at least 32 characters long`

**Solution:** Generate a new JWT_SECRET using `generate_keys.py`

### CORS Errors

If frontend can't connect to API:

**Solution:** Verify `CORS_ORIGINS` includes your frontend domain

### Database Connection Issues

**Solution:** 
- Verify DATABASE_URL format
- Check database is accessible
- Verify credentials

### Missing Encryption Key

If OAuth features don't work:

**Solution:** Generate ENCRYPTION_KEY using `generate_keys.py`

## Support

For issues or questions, refer to:
- README.md - General documentation
- SETUP_GUIDE.md - Development setup
- API Documentation - http://localhost:8000/docs (or your production URL)

