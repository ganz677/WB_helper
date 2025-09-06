from abc import ABC, abstractmethod

class LLM(ABC):
    @abstractmethod
    async def short_reply(self, text: str, tone: str = 'neutral') -> str: ...