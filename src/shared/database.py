import logging

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing_extensions import AsyncGenerator


class PostgresSession:
    _engine = None
    _async_session_maker = None

    @classmethod
    async def init(cls, database_url: str):
        """Initialize the database engine — call this once at startup."""
        cls._engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=20,
            max_overflow=10,
            echo=False,
            connect_args={"server_settings": {"client_encoding": "UTF-8"}},
        )
        cls._async_session_maker = async_sessionmaker(
            cls._engine, class_=AsyncSession, expire_on_commit=False
        )

    @classmethod
    async def get_session(cls) -> AsyncSession:
        """Get a new session for each operation."""
        if cls._async_session_maker is None:
            raise RuntimeError("Database not initialized. Call init() first.")
        return cls._async_session_maker()

    @classmethod
    async def close(cls):
        """Close the engine — call this at shutdown."""
        if cls._engine:
            await cls._engine.dispose()


async def get_db(request: Request) -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency — yields a session with automatic cleanup."""
    async with await PostgresSession.get_session() as session:
        try:
            yield session
        except Exception as e:
            logging.debug(f"Rolling back due to exception {e}.")
            await session.rollback()
            raise e
        finally:
            await session.close()
