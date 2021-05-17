import sys
from loguru import logger

from .settings import GeneralSettings

LoggerFormat = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
               "<level>{level}</level> | " \
               "<level>{message}</level> | " \
               "{extra} {exception}"

logger.remove()
logger.add(
    sys.stderr,
    level=GeneralSettings().log_level.upper(),
    format=LoggerFormat,
    diagnose=False
)
