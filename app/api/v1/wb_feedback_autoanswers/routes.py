from fastapi import APIRouter
from app.mq.celery_app import celery
from .schemas import GenerateRequest, SendRequest

router = APIRouter(
    prefix='/feedbacks'
)

@router.post(
    path='/sync'
)
async def sync_feedbacks():
    celery.send_task("feedbacks.fetch_new", queue="fetch")
    return {
        'queued': True,
    }

@router.post(
    path='/{item_id}/generate'
)
async def generate_answer(item_id: int, body: GenerateRequest):
    celery.send_task("feedbacks.generate", args=[item_id, body.text], queue="llm")
    return {
        'queued': True,
    }

@router.post(
    path='/{item_id}/send'
)
async def send_answer(item_id: int, body: SendRequest):
    celery.send_task("feedbacks.send", args=[item_id, body.text], queue="send")
    return {
        'queued': True,
    }