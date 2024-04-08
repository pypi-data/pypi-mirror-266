import json
import logging
import sys
import typing

try:
    from qstd_async_tools.trace import get_trace_ids
except ImportError:
    def get_trace_ids() -> typing.Optional[typing.List[str]]:
        pass


class LogRecord(logging.LogRecord):
    payload: typing.Any
    trace_ids: typing.Optional[typing.List[str]]


class JsonFormatter(logging.Formatter):
    datefmt = None
    default_time_format = "%Y-%m-%dT%H:%M:%S"
    msec_format = "%s.%03dZ"

    FORMATTERS: typing.Dict[str, typing.Callable[[LogRecord], dict]] = dict()
    ROOT_FORMATTERS: typing.Dict[str, typing.Callable[[LogRecord], dict]] = dict()
    PARSE_PAYLOAD_ROOT_LOGGER: typing.Set[str] = set()

    def __init__(self):
        super().__init__()

    @classmethod
    def set_formatter(cls, name: str, dict_formatter: typing.Callable[[LogRecord], dict]):
        cls.FORMATTERS[name] = dict_formatter
        return cls

    @classmethod
    def set_root_formatter(cls, name: str, dict_formatter: typing.Callable[[LogRecord], dict]):
        cls.ROOT_FORMATTERS[name] = dict_formatter
        return cls

    @classmethod
    def set_parse_payload_root_logger(cls, name: str):
        cls.PARSE_PAYLOAD_ROOT_LOGGER.add(name)
        return cls

    @classmethod
    def default_formatter(cls, record: LogRecord) -> dict:
        return dict(
            level=record.levelname,
            message=record.message,
            label=record.name,
            pname=record.processName,
            pid=record.process,
            timestamp=record.asctime
        )

    def format(self, record: LogRecord) -> str:
        root_name = record.name.split('.')[0]
        if root_name in self.PARSE_PAYLOAD_ROOT_LOGGER:
            record.message = record.msg
            if not record.args:
                record.payload = None
            elif len(record.args) == 1:
                record.payload = record.args[0]
            else:
                record.payload = record.args
        else:
            record.message = record.getMessage()
            record.payload = None
        record.asctime = self.formatTime(record, self.datefmt)
        record.trace_ids = get_trace_ids()
        if record.name in self.FORMATTERS:
            log_dict = self.FORMATTERS[record.name](record)
        elif root_name in self.ROOT_FORMATTERS:
            log_dict = self.ROOT_FORMATTERS[root_name](record)
        else:
            log_dict = self.default_formatter(record)
        if record.payload:
            log_dict['payload'] = record.payload
        if record.trace_ids:
            log_dict['trace_ids'] = record.trace_ids
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            log_dict["exc_info"] = record.exc_text
        if record.stack_info:
            log_dict["stack_info"] = self.formatStack(record.stack_info)
        return json.dumps(log_dict, default=str)


def configure(formatter_cls: typing.Type[JsonFormatter]):
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter_cls())
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
