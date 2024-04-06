import logging

import structlog

from ujson import dumps
from structlog.dev import (
    Column,
    KeyValueColumnFormatter,
    BRIGHT,
    DIM,
    CYAN,
    RESET_ALL,
    RED,
    YELLOW,
    GREEN,
    RED_BACK,
)

from kilmlogger.constants import (
    ACCEPTED_LEVELS,
    DEFAULT_FILE_LOG,
    REPLACE_KEY_FOR_TIMESTAMP,
    REPLACE_KEY_FOR_EVENT,
    TIME_FIELD_NAME,
    MESSAGE_FIELD_NAME,
    LEVEL_FIELD_NAME,
    CORRELATION_FIELD_NAME,
    EXTRA_DATA_FIELD_NAME,
    METRICS_FIELD_NAME,
)
from kilmlogger.utils import add_correlation
from kilmlogger.styles import LogLevelColumnFormatter
from kilmlogger.envs import envs


LOG_LEVEL_COLORS = {
    "critical": RED,
    "exception": RED,
    "error": RED,
    "warn": YELLOW,
    "warning": YELLOW,
    "info": GREEN,
    "debug": GREEN,
    "notset": RED_BACK,
}


class KilmLoggerConfiguration:
    def __init__(
        self,
        logging_filename: str = DEFAULT_FILE_LOG,
        logging_level: int = logging.INFO,
        accepted_levels: list[str] = ACCEPTED_LEVELS,
        console_logging_level: int = logging.INFO,
        use_async: bool = False,
    ) -> None:
        self.logging_filename = logging_filename
        self.logging_level = logging_level
        self.accepted_levels = accepted_levels
        self.console_logging_level = console_logging_level
        self.formatters = self._use_default_formatters()
        self.handlers = self._use_default_handlers()
        self.loggers = self._use_default_loggers()
        self.use_async = use_async

    def use_default_configuration(self) -> None:
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": self.formatters,
                "handlers": self.handlers,
                "loggers": self.loggers,
            }
        )

        self._config_structlog()

    def _config_structlog(self) -> None:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_log_level,
                add_correlation,
                structlog.processors.TimeStamper(
                    fmt=envs.TIME_FORMAT, key=REPLACE_KEY_FOR_TIMESTAMP
                ),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.EventRenamer(to=REPLACE_KEY_FOR_EVENT),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            wrapper_class=structlog.stdlib.AsyncBoundLogger if self.use_async else structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def _use_default_formatters(self) -> dict:
        return {
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.dev.ConsoleRenderer(
                        colors=True,
                        columns=[
                            Column(
                                "",
                                KeyValueColumnFormatter(
                                    key_style=None,
                                    value_style=DIM,
                                    reset_style=RESET_ALL,
                                    value_repr=str,
                                ),
                            ),
                            Column(
                                TIME_FIELD_NAME,
                                KeyValueColumnFormatter(
                                    key_style=None,
                                    value_style=RESET_ALL,
                                    reset_style=RESET_ALL,
                                    value_repr=str,
                                ),
                            ),
                            Column(
                                LEVEL_FIELD_NAME,
                                LogLevelColumnFormatter(
                                    LOG_LEVEL_COLORS, reset_style=RESET_ALL
                                ),
                            ),
                            Column(
                                CORRELATION_FIELD_NAME,
                                KeyValueColumnFormatter(
                                    key_style=None,
                                    value_style=CYAN,
                                    reset_style=RESET_ALL,
                                    value_repr=str,
                                    width=30,
                                ),
                            ),
                            Column(
                                MESSAGE_FIELD_NAME,
                                KeyValueColumnFormatter(
                                    key_style=None,
                                    value_style=BRIGHT,
                                    reset_style=RESET_ALL,
                                    value_repr=str,
                                ),
                            ),
                            Column(
                                EXTRA_DATA_FIELD_NAME,
                                KeyValueColumnFormatter(
                                    key_style=None,
                                    value_style=BRIGHT,
                                    reset_style=RESET_ALL,
                                    value_repr=str,
                                ),
                            ),
                            Column(
                                METRICS_FIELD_NAME,
                                KeyValueColumnFormatter(
                                    key_style=None,
                                    value_style=BRIGHT,
                                    reset_style=RESET_ALL,
                                    value_repr=str,
                                ),
                            ),
                        ],
                    ),
                ],
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(serializer=dumps, ensure_ascii=False),
                "foreign_pre_chain": [
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                ],
            },
        }

    def _use_default_handlers(self) -> dict:
        return {
            "default": {
                "level": self.console_logging_level,
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
            "file": {
                "level": logging.DEBUG,
                "class": "logging.handlers.WatchedFileHandler",
                "filename": self.logging_filename,
                "formatter": "json",
            },
            "scribe": {
                "level": self.logging_level,
                "class": "kilmlogger.handler.GRPCEventStreamingHandler",
                "accepted_levels": self.accepted_levels,
            },
        }

    def _use_default_loggers(self) -> dict:
        return {
            "kilmlogger": {
                "handlers": ["default", "file", "scribe"],
                "level": logging.DEBUG,
                "propagate": True,
            },
        }
