import datetime
import json
import os
from logging import Formatter, LogRecord

from setech.utils import SetechJSONEncoder


class LogJSONFormatter(Formatter):
    default_time_format = "%Y-%m-%d %H:%M:%S"

    def format(self, record: LogRecord) -> str:
        record_default_keys = [
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "exc_info",
            "filename",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "asctime",
            "module",
            "exc_text",
            "stack_info",
        ]
        structured_data = dict(
            app=os.environ.get("APP_NAME", "dev"),
            level=record.levelname,
            name=record.name,
            date_time=datetime.datetime.fromtimestamp(record.created).strftime(self.default_time_format),
            location=f"{record.pathname or record.filename}:{record.funcName}:{record.lineno}",
            message=record.getMessage(),
            extra_data={k: record.__dict__[k] for k in record.__dict__.keys() if k not in record_default_keys},
        )

        return json.dumps(structured_data, cls=SetechJSONEncoder)
