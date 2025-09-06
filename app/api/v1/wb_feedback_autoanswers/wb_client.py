import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from redis.asyncio import Redis

from app.core.settings import settings
from app.limiter.token_bucket import TokenBucket
from app.observability.metrics import wb_responses



class WBFeedbacksClient:
    def __init__(self, redis: Redis):
        self._redis = redis
        self._http = httpx.AsyncClient(
            base_url=settings.wb.base_url,
            headers={'Authorization': settings.wb.token},
            timeout=20.0,
        )
        self._bucket = TokenBucket(
            self._redis,
            'wb_feedbacks',
            settings.wb.rps,
            settings.wb.burst,
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.2, min=0.5, max=5),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.RequestError))
    )
    async def list_feedbacks(self, params: dict) -> dict:
        await self._bucket.acquire()
        r = await self._http.get('/api/v1/feedbacks', params=params)
        wb_responses.labels('feedbacks_list', str(r.status_code)).inc()
        r.raise_for_status()
        return r.json()
    

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.2, min=0.5, max=5),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.RequestError))
    )
    async def answer_feedback(self, feedback_id: int, text: str) -> dict:
        await self._bucket.acquire()
        payload = {
            'id': feedback_id,
            'text': text,  
        }
        r = await self._http.post('/api/v1/feedbacks/answer', json=payload)
        wb_responses.labels('feedbacks_answer', str(r.status_code)).inc()
        r.raise_for_status()
        return r.json()
    
    async def aclose(self):
        await self._http.aclose()

