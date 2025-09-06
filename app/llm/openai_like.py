import httpx
from app.core.settings import settings
from .base import LLM


class OpenAILike(LLM):
    def __init__(self):
        self._http = httpx.AsyncClient(
            base_url=settings.llm.base_url,
            headers={
                'Authorization': f'Bearer {settings.llm.api_key}'
            },
            timeout=30.0
        )

    async def short_reply(self, text: str, tone = 'neutral') -> str:
        system = (
            "Ты пишешь короткие и вежливые ответы для маркетплейса. "
            "Не обещай недоступного. 1–2 предложения, 30–200 символов."
        )
        body = {
            'model': settings.llm.model,
            'messages': [
                {'role': 'system', 'content' : system},
                {'role': 'user', 'content': f'Тон: {tone}. Текст: {text}'}
            ],
            'temperature': 0.4,
            'max_tokens': 120, 
        }
        r = await self._http.post('/chat/completions', json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    async def aclose(self):
        await self._http.aclose()