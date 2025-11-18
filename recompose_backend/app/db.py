# --- Database Module ---
"""
Database connection and session management using async SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# --- Database Engine ---
# Configure connection args for PostgreSQL (including Neon)
connect_args = {}
if "postgresql" in settings.DATABASE_URL:
    connect_args = {
        "server_settings": {
            "application_name": settings.APP_NAME,
        },
        "command_timeout": int(settings.DB_CONNECT_TIMEOUT),
    }
    # Add SSL mode for Neon PostgreSQL (requires SSL)
    # asyncpg expects ssl parameter as string or SSL context, not boolean
    if "neon" in settings.DATABASE_URL.lower() or settings.DB_SSL_MODE != "disable":
        if settings.DB_SSL_MODE == "require":
            connect_args["ssl"] = "require"
        elif settings.DB_SSL_MODE == "prefer":
            connect_args["ssl"] = "prefer"
        elif settings.DB_SSL_MODE == "allow":
            connect_args["ssl"] = "allow"
        # "disable" is handled by not setting ssl parameter

# Configure engine parameters
# SQLite doesn't support pool_size, max_overflow, or pool_recycle
engine_kwargs = {
    "echo": settings.DEBUG,  # Log SQL queries in debug mode
    "future": True,
    "pool_pre_ping": True,  # Verify connections before using (handles reconnection)
    "connect_args": connect_args,
}

# Only add pool settings for PostgreSQL (not SQLite)
if "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL:
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# --- Session Factory ---
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# --- Base Model Class ---
Base = declarative_base()


# --- Database Dependency ---
async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

