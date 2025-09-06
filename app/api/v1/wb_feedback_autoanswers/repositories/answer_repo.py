from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.db_helper import db_helper
from app.core.models import Answer


class AnswerRepo:
    def __init__(
        self,
        db: AsyncSession
    ) -> None:
        self.db = db
        self.model = Answer

    async def create(self, ans: Answer) -> Answer:
        self.db.add(ans)
        await self.db.flush()     
        return ans                

    async def by_item(self, item_id: int) -> list[Answer]:
        query = select(self.model).where(self.model.item_id == item_id)
        return (await self.db.execute(query)).scalars().all()
