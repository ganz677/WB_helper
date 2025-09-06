from pydantic import BaseModel


class RequestBase(BaseModel):
    text: str

class GenerateRequest(RequestBase):
    tone: str | None = None


class SendRequest(RequestBase):
    pass