# ReCompose AI Backend

Production-grade FastAPI backend for ReCompose AI, a SaaS tool that rewrites user emails to sound clear, polite, and professional using OpenAI GPT-4o.

## Features

- **JWT Authentication**: Secure user signup and login with JWT tokens (24h expiration)
- **Email Rewriting**: AI-powered email rewriting with customizable tones (friendly, professional, persuasive)
- **Usage Logging**: Track all rewrites with analytics (word count, token usage, timestamps)
- **PostgreSQL Database**: Async SQLAlchemy with Alembic migrations
- **OpenAPI Documentation**: Auto-generated Swagger UI at `/docs`
- **CORS Enabled**: Ready for frontend integration
- **Comprehensive Tests**: Unit tests for authentication and rewrite endpoints

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL (via SQLAlchemy async)
- Alembic (migrations)
- JWT authentication (python-jose)
- OpenAI GPT-4o API
- Pydantic (validation)
- pytest (testing)

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- OpenAI API key

### 2. Installation

```bash
# Navigate to backend directory
cd recompose_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the `recompose_backend` directory. Copy `.env.example` as a template:

```bash
cp .env.example .env
```

Then edit `.env` and set your values. Required variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key (required, validated at startup)
- `JWT_SECRET`: Secret key for JWT tokens (required, must be at least 32 characters in production)

Optional variables:
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: `http://localhost:3000`)
- `BILLING_ENABLED`: Set to `true` to enable billing endpoints (default: `false`)

See `.env.example` for all available options and descriptions.

### 4. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 5. Start the Server

**Linux/Mac:**
```bash
chmod +x start_app.sh
./start_app.sh
```

**Windows PowerShell:**
```powershell
.\start_app.ps1
```

**Or manually:**
```bash
# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/signup` - Create a new user account
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info (protected)

### Rewrite

- `POST /rewrite` - Rewrite an email (protected)
  - Request body:
    ```json
    {
      "email_text": "Your email text here",
      "tone": "professional"  // or "friendly" or "persuasive"
    }
    ```
  - Response:
    ```json
    {
      "rewritten_email": "Rewritten email text"
    }
    ```

- `GET /rewrite/logs` - Get rewrite history (protected)
  - Query parameters:
    - `limit` (optional): Number of logs to return (1-100, default: 20)
    - `offset` (optional): Number of logs to skip for pagination (default: 0)
  - Response:
    ```json
    {
      "logs": [
        {
          "id": 1,
          "original_email": "Original email text",
          "rewritten_email": "Rewritten email text",
          "tone": "professional",
          "word_count": 25,
          "token_used": 150,
          "created_at": "2024-01-01T12:00:00"
        }
      ],
      "total": 1,
      "limit": 20,
      "offset": 0
    }
    ```

### Billing

- `POST /billing/subscribe` - Subscribe to a plan (placeholder for Stripe integration)
  - **Note**: Billing endpoints are disabled by default. Set `BILLING_ENABLED=true` in your `.env` file to enable.
  - When disabled, endpoints return `503 Service Unavailable`.

## Testing

Run tests with pytest:

```bash
pytest app/tests/
```

Run with coverage:

```bash
pytest app/tests/ --cov=app
```

## Project Structure

```
recompose_backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── db.py                # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   └── rewrite.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   ├── rewrite.py
│   │   └── billing.py
│   ├── core/                # Core utilities
│   │   ├── security.py      # JWT & password hashing
│   │   └── utils.py         # Helper functions
│   └── tests/               # Test files
│       ├── test_auth.py
│       └── test_rewrite.py
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── start_app.sh             # Startup script (Linux/Mac)
├── start_app.ps1            # Startup script (Windows)
└── .env.example             # Environment variables template
```

## Development

### Creating Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Environment Variables

All configuration is done via environment variables. See `.env.example` for all available options.

## Security Notes

- **JWT Secret**: Change `JWT_SECRET` in production to a strong random string (minimum 32 characters)
- **Database**: Use strong passwords and restrict database access
- **OpenAI API Key**: Required and validated at startup. Keep your API key secure and never commit it to version control
- **CORS**: Configure `CORS_ORIGINS` environment variable with comma-separated list of allowed origins for production

## License

Proprietary - All rights reserved

