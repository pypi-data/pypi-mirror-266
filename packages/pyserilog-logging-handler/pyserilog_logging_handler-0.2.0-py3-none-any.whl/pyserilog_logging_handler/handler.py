import logging
import threading
from datetime import datetime
from logging import LogRecord

from pyserilog import LoggerConfiguration
from pyserilog.core.constants import Constants
from pyserilog.core.logger import Logger
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel


class Handler(logging.Handler):
    __context_loggers: dict[str, Logger] = {}
    _locker = threading.Lock()

    def __init__(self, logger_configuration: LoggerConfiguration):
        super().__init__()
        self._logger: Logger = logger_configuration.create_logger()
        self.formatter = None
        self.name = "PyserilogLogHandler"

    def emit(self, record: LogRecord) -> None:
        logger = self.__get_logger(record.name)
        event = Handler._make_log_event(logger, record)
        if event:
            logger.write_event(event)

    @staticmethod
    def _make_log_event(logger: Logger, record: LogRecord) -> LogEvent:
        property_values = []
        level_number = Handler._get_level(record.levelno)
        if record.args:
            for arg in record.args:
                property_values.append(arg)
        (checked, parsed_template, bound_properties) = logger.bind_message_template(record.msg, property_values)
        if checked:
            return LogEvent(
                timestamp=datetime.fromtimestamp(record.created),
                level=level_number,
                message_template=parsed_template,
                exception=record.exc_info,
                properties=bound_properties
            )
        return None

    @staticmethod
    def _get_level(record_level: int) -> LogEventLevel:
        match record_level:
            case logging.NOTSET:
                return LogEventLevel.VERBOSE
            case logging.DEBUG:
                return LogEventLevel.DEBUG
            case logging.INFO:
                return LogEventLevel.INFORMATION
            case logging.WARNING:
                return LogEventLevel.WARNING
            case logging.ERROR:
                return LogEventLevel.ERROR
            case logging.CRITICAL:
                return LogEventLevel.FATAL
        raise ValueError(f"Logging log level not found loglevel number = {record_level}")

    def __get_logger(self, name: str) -> Logger:
        if name in self.__context_loggers:
            return self.__context_loggers[name]
        with self._locker:
            if name in self.__context_loggers:
                return self.__context_loggers[name]
            logger = self._logger.for_context(Constants.SOURCE_CONTEXT_PROPERTY_NAME, name)
            self.__context_loggers[name] = logger
            return logger
