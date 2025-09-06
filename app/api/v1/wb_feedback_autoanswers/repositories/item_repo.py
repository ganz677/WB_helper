from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.db_helper import db_helper
from app.core.models import Item


class ItemRepo:
    def __init__(
        self,
        db: AsyncSession
    ) -> None:
        self.db = db
        self.model = Item

    async def upsert(self, item: Item) -> None:
        existing = await self.db.get(self.model, item.id)
        if existing:
            existing.payload = item.payload
            existing.created_at = item.created_at
            existing.nm_id = item.nm_id
        else:
            self.db.add(item) 

    async def mark_answered(self, item_id: int) -> None:
        await self.db.execute(
            update(self.model)
            .where(self.model.id == item_id)
            .values(answered=True)
        )

    async def get_unanswered(self, limit: int = 100) -> list[Item]:
        query = (
            select(self.model)
            .where(self.model.answered.is_(False))
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        return (await self.db.execute(query)).scalars().all()
