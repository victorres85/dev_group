import json
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from settings import BASE_DIR

class JsonFormatter(logging.Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        json_record = {
            "level": record.levelname,
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "message": record.getMessage(),
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName
        }
        return json.dumps(json_record)

logger = logging.getLogger('my_logger')

# Handler for INFO level logs
info_handler = TimedRotatingFileHandler(f'{BASE_DIR}/logs/info.log', when='midnight', interval=7, backupCount=5)
info_handler.setFormatter(JsonFormatter())
info_handler.setLevel(logging.INFO)

# Handler for ERROR level logs
error_handler = TimedRotatingFileHandler(f'{BASE_DIR}/logs/error.log', when='midnight', interval=7, backupCount=5)
error_handler.setFormatter(JsonFormatter())
error_handler.setLevel(logging.ERROR)

logger.handlers = [info_handler, error_handler]
logger.setLevel(logging.DEBUG)