import logging
import logging.config
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

from app.core.config import Settings

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)
        log_record.setdefault("request_id", getattr(record, "request_id", "-"))


def configure_logging(settings: Settings) -> None:
    formatter_class = (
        "app.core.logging.JsonFormatter"
        if settings.log_format == "json"
        else "logging.Formatter"
    )
    format_string = (
        "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
        if settings.log_format == "text"
        else "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
    )

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id_filter": {
                "()": "app.core.logging.RequestIdFilter",
            }
        },
        "formatters": {
            "default": {
                "()": formatter_class,
                "format": format_string,
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "filters": ["request_id_filter"],
            }
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["default"],
        },
    }

    logging.config.dictConfig(logging_config)
