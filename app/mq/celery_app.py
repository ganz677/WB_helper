from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init

from app.core.settings import settings
from app.core.models.db_helper import db_helper

celery = Celery(
    "wb",
    broker=settings.redis.url,
    backend=settings.redis.url,
)

celery.conf.update(
    imports=("app.mq.tasks_feedbacks",),
    task_routes={
        "feedbacks.fetch_new": {"queue": "fetch"},
        "feedbacks.generate": {"queue": "llm"},
        "feedbacks.send": {"queue": "send"},
    },
    task_acks_late=True,
    broker_transport_options={"visibility_timeout": 3600},
    timezone="UTC",
    beat_schedule={
        "fetch-feedbacks-every-5m": {
            "task": "feedbacks.fetch_new",
            "schedule": crontab(minute="*/5"),
        },
    },
)


@worker_process_init.connect
def _init_worker_process(**kwargs):
    db_helper.reset()
