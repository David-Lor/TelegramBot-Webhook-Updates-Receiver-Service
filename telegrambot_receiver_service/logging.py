import sys
from loguru import logger

from telegrambot_receiver_service.settings import general_settings

LoggerFormat = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
               "<level>{level}</level> | " \
               "<level>{message}</level> | " \
               "{extra} {exception}"

logger.remove()
logger.add(
    sys.stderr,
    level=general_settings.log_level.upper(),
    format=LoggerFormat,
    diagnose=False
)
