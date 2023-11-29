import os
import asyncio
from telegram.ext import ApplicationBuilder
from PIL import Image

from logger import Logger


class Telegram:
    def __init__(self, debug: bool = False):
        # asyncio.ensure_future(self.send_message())
        self.image_sent_failed_ctr = 0
        self.message_sent_failed_ctr = 0
        self.telegram_api_key = os.environ.get(f'TELEGRAM_API_KEY', 'token')
        self.telegram_chat_id = os.environ.get(f'TELEGRAM_CHAT_ID', 'chat_id')
        self.logger = Logger(debug=debug)
        self.bot = ApplicationBuilder().token(self.telegram_api_key).build().bot

    async def send_message(self, message: str):
        if self.message_sent_failed_ctr > 5:
            self.logger.error_message(
                f'message sending failed more than 5 times')
            return
        try:
            self.logger.info_message(f'{__name__} sending message')
            self.logger.debug_message(
                f'message: {message}')
            await self.bot.sendMessage(
                chat_id=self.telegram_chat_id,
                text=message
            )
        except Exception as error:
            self.logger.error_message(f'{__name__} message sending failed')
            self.logger.error_message(
                f'{__name__} error: {error}')
            self.message_sent_failed_ctr += 1
            self.send_message(message=message)
        self.message_sent_failed_ctr = 0

    async def send_image(self, message: str, image: bytes):
        if self.image_sent_failed_ctr > 5:
            self.logger.error_message(
                f'{__name__} image sending failed more than 5 times')
            return
        try:
            self.logger.info_message(f'{__name__} sending message')
            self.logger.debug_message(
                f'message: {message}')
            await self.bot.send_photo(
                chat_id=self.telegram_chat_id,
                photo=image,
                caption=message
            )
        except Exception as error:
            self.logger.error_message(f'{__name__} image sending failed')
            self.logger.error_message(
                f'{__name__} error: {error}')
            self.image_sent_failed_ctr += 1
            self.send_image(message=message, image=image)
        self.image_sent_failed_ctr = 0
