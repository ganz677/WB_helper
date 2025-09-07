import datetime
import asyncio
from typing import Any

class FakeWBFeedbacksClient:
    """
    Фейковый клиент WB для локальных e2e-тестов без реального API/токена.
    Интерфейс совместим с реальным WBFeedbacksClient:
      - __init__(redis, base_url, token, rps, burst)
      - list_feedbacks(params) -> dict
      - answer_feedback(feedback_id, text) -> dict
      - aclose()
    """

    def __init__(self,
                 redis: Any | None = None,
                 base_url: str | None = None,
                 token: str | None = None,
                 rps: int = 3,
                 burst: int = 6) -> None:
        # Сохраняем, если захочешь логировать/лимитить. Здесь можно игнорировать.
        self.redis = redis
        self.base_url = base_url
        self.token = token
        self.rps = rps
        self.burst = burst

    async def list_feedbacks(self, params: dict) -> dict:
        # Имитируем сетевую задержку
        await asyncio.sleep(0.05)
        # Возвращаем один «отзыв», как будто пришёл из WB
        return {
            "feedbacks": [
                {
                    "id": 123,
                    "nmId": 456,
                    "createdDate": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "text": "Тестовый отзыв: всё супер, спасибо!",
                }
            ]
        }

    async def answer_feedback(self, feedback_id: int, text: str) -> dict:
        # Имитируем отправку; можно писать в лог
        print(f"[FAKE WB] отправлен ответ для {feedback_id}: {text}")
        await asyncio.sleep(0.02)
        # Сымитируем форму ответа, близкую к реальной
        return {"ok": True, "feedbackId": feedback_id}

    async def aclose(self) -> None:
        # Нечего закрывать, но интерфейс должен быть совместим
        pass
