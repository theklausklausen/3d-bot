import os
import asyncio
from telegram.ext import ApplicationBuilder
from PIL import Image

from logger import Logger


class Telegram:
    def __init__(self, debug: bool = False):
        # asyncio.ensure_future(self.send_message())
        self.telegram_api_key = os.environ.get('TELEGRAM_API_KEY', 'token')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', 'chat_id')
        self.logger = Logger(debug=debug)
        self.bot = ApplicationBuilder().token(self.telegram_api_key).build().bot

    async def send_message(self, message: str):
        self.logger.info_message('sending message')
        self.logger.debug_message('message: {message}'.format(message=message))
        await self.bot.sendMessage(
            chat_id=self.telegram_chat_id,
            text=message
        )

    async def send_image(self, message: str, image: bytes):
        self.logger.info_message('sending message')
        self.logger.debug_message('message: {message}'.format(message=message))
        await self.bot.send_photo(
            chat_id=self.telegram_chat_id,
            photo=image,
            caption=message
        )
