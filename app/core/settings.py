import os 
from typing import Literal
from dotenv import load_dotenv

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"

class RunSettings(BaseModel):
    host: str = '127.0.0.1'
    port: int = 8000
    reload: bool = True

class DataBaseSettings(BaseModel):
    url: PostgresDsn
    echo: bool 
    echo_pool: bool 
    pool_size: int 
    max_overflow: int 
    pool_timeout: int 


class RedisSettings(BaseModel):
    url: str

class WBSettings(BaseModel):
    token: str
    base_url: str
    rps: int
    burst: int

class LLMSettings(BaseModel):
    base_url: str
    api_key: str
    model: str

class SentrySettings(BaseModel):
    dsn: str

class MetrixSettings(BaseModel):
    otlp_endpoint: str
    feature_auto_send: bool

class LoggingSettings(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'info'
    log_format: str = LOG_DEFAULT_FORMAT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP__',
        env_nested_delimiter='__',
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore',
        populate_by_name=True
    )
    db: DataBaseSettings
    redis: RedisSettings
    wb: WBSettings
    llm: LLMSettings
    sentry: SentrySettings
    metrix: MetrixSettings
    logging_config: LoggingSettings = LoggingSettings()
    run: RunSettings = RunSettings()

settings = Settings()

