# app/mq/tasks_feedbacks.py
import asyncio
from typing import Awaitable, Any

from redis.asyncio import Redis

from app.core.settings import settings
from .celery_app import celery
from app.core.models.db_helper import db_helper
from app.llm.openai_like import OpenAILike

from app.api.v1.wb_feedback_autoanswers.fake_wb_client import (
    FakeWBFeedbacksClient as WBFeedbacksClient,
)
from app.api.v1.wb_feedback_autoanswers.ingest_service import FeedbackUseCases


_LOOP: asyncio.AbstractEventLoop | None = None


def _get_loop() -> asyncio.AbstractEventLoop:
    """
    Возвращаем один и тот же loop внутри текущего процесса воркера.
    Не создаём ничего на импорте (чтобы не ломаться при prefork).
    """
    global _LOOP
    if _LOOP is None or _LOOP.is_closed():
        _LOOP = asyncio.new_event_loop()
        asyncio.set_event_loop(_LOOP)
    return _LOOP


def _run(coro: Awaitable[Any]) -> Any:
    """Запускаем корутины всегда в ОДНОМ loop текущего процесса."""
    loop = _get_loop()
    return loop.run_until_complete(coro)


@celery.task(name="feedbacks.fetch_new")
def fetch_new():
    _run(_fetch_new_async())


async def _fetch_new_async():
    redis = Redis.from_url(settings.redis.url)
    wb = WBFeedbacksClient(redis)
    async with db_helper.session() as session:
        use = FeedbackUseCases(db=session, wb=wb)
        await use.ingest_recent_feedbacks()
    await wb.aclose()
    await redis.aclose()


@celery.task(name="feedbacks.generate")
def generate(item_id: int, text: str):
    _run(_generate_async(item_id, text))


async def _generate_async(item_id: int, text: str):
    llm = OpenAILike()
    redis = Redis.from_url(settings.redis.url)
    wb = WBFeedbacksClient(redis)
    async with db_helper.session() as session:
        use = FeedbackUseCases(db=session, wb=wb, llm=llm)
        await use.generate_short_answer(
            item_id=item_id, text=text, provider_name="openai_like"
        )
    await llm.aclose()
    await wb.aclose()
    await redis.aclose()


@celery.task(name="feedbacks.send")
def send(item_id: int, text: str):
    _run(_send_async(item_id, text))


async def _send_async(item_id: int, text: str):
    redis = Redis.from_url(settings.redis.url)
    wb = WBFeedbacksClient(redis)
    async with db_helper.session() as session:
        use = FeedbackUseCases(db=session, wb=wb)
        await use.send_answer_for_feedback(item_id=item_id, text=text)
    await wb.aclose()
    await redis.aclose()
