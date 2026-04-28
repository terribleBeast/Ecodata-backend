from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class PostgresSession:
    _engine = None
    _async_session_maker = None

    @classmethod
    async def init(cls, database_url: str):
        """Initialize the database engine - call this once at startup"""
        cls._engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=20,
            max_overflow=10,
            echo=False,
            connect_args={"server_settings": {"client_encoding": "WIN1251"}},
        )
        cls._async_session_maker = async_sessionmaker(
            cls._engine, class_=AsyncSession, expire_on_commit=False
        )

    @classmethod
    async def get_session(cls) -> AsyncSession:
        """Get a new session for each operation"""
        if cls._async_session_maker is None:
            raise RuntimeError("Database not initialized. Call init() first.")
        return cls._async_session_maker()

    @classmethod
    async def close(cls):
        """Close the engine - call this at shutdown"""
        if cls._engine:
            await cls._engine.dispose()
