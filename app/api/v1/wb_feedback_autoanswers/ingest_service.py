import json, datetime
from typing import TYPE_CHECKING, Annotated
from fastapi import Depends

from app.core.models import (
    Item,
    Answer,
    SourceType,
    db_helper
)
from .repositories.item_repo import ItemRepo
from .repositories.answer_repo import AnswerRepo
from .wb_client import WBFeedbacksClient
from app.llm.base import LLM
from app.observability.metrics import (
    items_ingested,
    answers_generated,
    answers_sent
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class FeedbackUseCases:
    def __init__(
            self,
            db: Annotated['AsyncSession', Depends(db_helper.session_getter)],
            wb: WBFeedbacksClient,
            llm: LLM | None = None,
        ):
        self.db = db
        self.items_repo = ItemRepo(db)
        self.answers_repo = AnswerRepo(db)
        self.wb = wb
        self.llm = llm

    async def ingest_recent_feedbacks(self) -> int:
        data = await self.wb.list_feedbacks(
            {
                "isAnswered": "false",
                "order": "dateDesc",
                "take": 1000
            }
        )
        rows = data.get("feedbacks") or data.get("data") or []
        count = 0
        for raw in rows:
            created_dt = None
            created = raw.get("createdDate")
            if isinstance(created, str):
                created_dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
            item = Item(
                id=int(raw.get("id")),
                source=SourceType.review,
                nm_id=raw.get("nmId"),
                created_at=created_dt or datetime.datetime.now(datetime.timezone.utc),
                payload=json.dumps(raw, ensure_ascii=False),
            )
            await self.items_repo.upsert(item)
            items_ingested.labels(SourceType.review.value).inc()
            count += 1
        await self.db.commit()
        return count
    
    async def generate_short_answer(
            self,
            item_id: int,
            text: str,
            provider_name: str
    ) -> Answer:
        assert self.llm is not None, 'LLM client is required'
        reply = await self.llm.short_reply(text)
        ans = Answer(
            item_id=item_id,
            text=reply,
            provider=provider_name
        )
        ans = await self.answers_repo.create(ans)
        await self.db.commit()
        answers_generated.labels(provider_name).inc()
        return ans
    
    async def send_answer_for_feedback(
            self,
            item_id: int,
            text: str
        ) -> None:
        await self.wb.answer_feedback(item_id, text)
        for ans in await self.answers_repo.by_item(item_id):
            if not ans.sent:
                ans.sent = True
                ans.sent_at = datetime.datetime.now(datetime.timezone.utc)
        await self.items_repo.mark_answered(item_id)
        await self.s.commit()
        answers_sent.labels(SourceType.review.value).inc()