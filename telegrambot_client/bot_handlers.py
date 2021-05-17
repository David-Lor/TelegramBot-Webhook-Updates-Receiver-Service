import telebot

from .logging import logger


def register_handlers(bot: telebot.TeleBot):
    @bot.message_handler(commands=["start"])
    def start_command_handler(msg, *args, **kwargs):
        logger.info("/start command received")
        bot.reply_to(msg, text="Hello there!")

    @bot.message_handler(commands=["help"])
    def help_command_handler(msg, *args, **kwargs):
        logger.info("/help command received")
        bot.reply_to(msg, text="I'm helping you!")
