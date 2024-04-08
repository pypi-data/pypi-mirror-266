

# Logging Json Formatter


```python
import logging
from qstd_logger_json_formatter import JsonFormatter, configure

JsonFormatter\
    .set_parse_payload_root_logger('app')\
    .set_formatter(
        'sanic.access',
        lambda record: dict(
            level=record.levelname,
            message=record.message,
            host=record.host,
            request=record.request,
            status=record.status,
            byte=record.byte,
            label=record.name,
            pname=record.processName,
            pid=record.process,
            timestamp=record.asctime
        )
    )

configure(JsonFormatter)

app_logger = logging.getLogger('app')

app_logger.info('Example message', dict(string='string', number=1))
```
