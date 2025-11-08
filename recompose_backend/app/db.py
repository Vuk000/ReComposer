# --- Database Module ---
"""
Database connection and session management using async SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# --- Database Engine ---
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Maximum overflow connections
    pool_pre_ping=True,  # Verify connections before using (handles reconnection)
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle connections after this many seconds
    connect_args={
        "server_settings": {
            "application_name": settings.APP_NAME,
        },
        "command_timeout": int(settings.DB_CONNECT_TIMEOUT),
    } if "postgresql" in settings.DATABASE_URL else {},
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

