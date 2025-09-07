from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import settings


class DataBaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool,
        echo_pool: bool,
        pool_size: int,
        max_overflow: int,
        pool_timeout: int,
    ) -> None:
        self.url = url
        self.echo = echo
        self.echo_pool = echo_pool
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout

        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def _ensure_engine(self) -> None:
        if self.engine is None:
            self.engine = create_async_engine(
                url=self.url,
                echo=self.echo,
                echo_pool=self.echo_pool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_pre_ping=True,
            )
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                autoflush=False,
                expire_on_commit=False,
            )

    def reset(self) -> None:
        self.engine = None
        self.session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        self._ensure_engine()
        assert self.session_factory is not None
        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()

    async def dispose(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()


db_helper = DataBaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    pool_timeout=settings.db.pool_timeout,
)
