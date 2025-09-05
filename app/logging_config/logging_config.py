import logging
import sys
from typing import Any, Mapping

import structlog
from pythonjsonlogger import jsonlogger

_LEVEL_MAP: Mapping[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _to_level(level_str: str) -> int:
    """Перевод 'info' → logging.INFO"""
    return _LEVEL_MAP.get(level_str.lower(), logging.INFO)


# === JSON форматер для uvicorn ===
class UvicornJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)
        log_record.setdefault("module", record.module)
        log_record.setdefault("funcName", record.funcName)
        log_record.setdefault("lineno", record.lineno)


def setup_logging(
    level: str = "info",
    json_logs: bool = True,
    text_format: str = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
) -> None:
    """
    Настройка логирования:
      - root и uvicorn логгеры переводятся на stdout
      - можно включить JSON (прод) или текст (локал)
      - structlog настроен на тот же уровень
    """
    lvl = _to_level(level)

    # базовый root logger
    root = logging.getLogger()
    root.setLevel(lvl)
    root.handlers.clear()

    # handler -> stdout
    handler = logging.StreamHandler(sys.stdout)
    if json_logs:
        handler.setFormatter(UvicornJsonFormatter("%(message)s"))
    else:
        handler.setFormatter(logging.Formatter(text_format, datefmt="%Y-%m-%d %H:%M:%S"))
    root.addHandler(handler)

    # uvicorn loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.setLevel(lvl)
        lg.propagate = False
        lg.addHandler(handler)

    # structlog config
    if json_logs:
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.dict_tracebacks,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(lvl),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
