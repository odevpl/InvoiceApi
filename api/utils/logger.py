import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import json

from api.config.settings import settings


LOG_DIR_PATH = Path(settings.LOG_DIR)
LOG_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR_PATH / "api.json"

LOG_LEVEL = settings.LOG_LEVEL
BACKUP_COUNT = settings.LOG_BACKUP_COUNT


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # structured extras
        if hasattr(record, "req"):
            log["req"] = record.req
        if hasattr(record, "res"):
            log["res"] = record.res

        # exception if exists
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, ensure_ascii=False)


logger = logging.getLogger("api")
logger.setLevel(LOG_LEVEL)

file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=BACKUP_COUNT,
    encoding="utf-8")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)
logger.propagate = False
