from loguru import logger

from telegrambot_receiver_service.settings import general_settings


logger.level(general_settings.log_level.upper())
