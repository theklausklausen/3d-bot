import asyncio
import os
import time
import datetime
import logging
from dotenv import load_dotenv
import sys
# import subprocess

from octopi import OctoPi
from job import Job
from logger import Logger
from telegram_client import Telegram
from errors import *
from sentry import init_sentry

telegram = octopi = job = None
debug = os.environ.get('DEBUG', default='False') == 'True'
logger = Logger(debug=debug)
module = import_path = script_path = None

init_sentry(debug=debug)

try:
    script_path = os.environ.get('CUSTOM_SCRIPT_PATH')
except EnvironmentError:
    pass

if script_path:
    if os.path.isfile(script_path):
        try:
            module = script_path.split('/')[-1].replace('.py', '')
            import_path = script_path.replace(
                '/{module}.py'.format(module=module), '')
        except Exception:
            logger.error_message(
                'CUSTOM_SCRIPT_PATH has to be like "/path/to/file.py"')
    else:
        raise ImportError('{script} not found'.format(script=script_path))

if module:
    sys.path.insert(1, import_path)

    # pre message command
    try:
        pre_message_command = getattr(__import__(
            module, fromlist=['pre_message_command']), 'pre_message_command')
        logger.info_message(message='found \"pre_message_command\" function')
    except AttributeError:
        logger.info_message(
            message='no \"pre_message_command\" function found, using default definition')

        def pre_message_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** pre message command ***')

    # post message command
    try:
        post_message_command = getattr(__import__(
            module, fromlist=['post_message_command']), 'post_message_command')
        logger.info_message(
            message='found \"post_message_command\" function')
    except AttributeError:
        logger.info_message(
            message='no \"post_message_command\" function found, using default definition')

        def post_message_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** post message command ***')

    # post finished command
    try:
        post_finished_command = getattr(__import__(
            module, fromlist=['post_finished_command']), 'post_finished_command')
        logger.info_message(
            message='found \"post_finished_command\" function')
    except AttributeError:
        logger.info_message(
            message='no \"post_finished_command\" function found, using default definition')

        def post_finished_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** post finished command ***')

    # post filament empty command
    try:
        on_filament_empty_command = getattr(__import__(
            module, fromlist=['on_filament_empty_command']), 'on_filament_empty_command')
        logger.info_message(
            message='found \"on_filament_empty_command\" function')
    except AttributeError:
        logger.info_message(
            message='no \"on_filament_empty_command\" function found, using default definition')

        def on_filament_empty_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** post on filament empty command ***')

    # on overheating command
    try:
        on_overheating_command = getattr(__import__(
            module, fromlist=['on_overheating_command']), 'on_overheating_command')
        logger.info_message(
            message='found \"on_overheating_command\" function')
    except AttributeError:
        logger.info_message(
            message='no \"on_overheating_command\" function found, using default definition')

        def on_overheating_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** on overheating command command ***')

else:
    def pre_message_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
        print('*** pre message command ***')

    def post_message_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
        print('*** post message command ***')

    def post_finished_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
        print('*** post finished command ***')

    def on_filament_empty_command(telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
        print('*** post on filament empty command ***')

class Runtime():
    telegram = Telegram(debug=debug)
    octopi = OctoPi(debug=debug)
    job = None
    if not debug:
        logging.getLogger('asyncio').setLevel(logging.INFO)

    async def send_state(self, prefix: str = ''):
        logger.info_message('sending state')
        message = '{prefix}The job of {file} has reached {completion:.2f}% of completion.\nFilament usage: ~ {current:.2f}m / {planned:.2f}m\nETA: {eta} hrs\n{link}'.format(
            prefix=prefix,
            file=self.job.file,
            completion=self.job.progress['completion'],
            eta=str(datetime.timedelta(
                seconds=self.job.progress['print_time_left'])),
            planned=(self.job.filament/1000),
            current=((self.job.filament*(self.job.progress['completion']*0.01))/1000),
            link=self.octopi.host
        )
        image = self.octopi.get_image()
        await self.telegram.send_image(message, image)

    async def main(self) -> None:
        load_dotenv()

        logger.info_message('starting up...')
        sleep_time = int(os.environ.get('SLEEP_TIME', '5'))

        while True:
            time.sleep(sleep_time)
            temp_is_ok = self.octopi.temp_is_ok()
            if (isinstance(temp_is_ok, bool) and not temp_is_ok):
                try:
                    pre_message_command(
                        telegram_client=self.telegram, job=self.job, octopi=self.octopi)
                except Exception as error:
                    logger.error_message(error)
                await self.send_state()
                try:
                    post_message_command(
                        telegram_client=self.telegram, job=self.job, octopi=self.octopi)
                except Exception as error:
                    logger.error_message(error)
                try:
                    on_overheating_command(
                        telegram_client=self.telegram, job=self.job, octopi=self.octopi)
                except Exception as error:
                    logger.error_message(error)
            self.job = self.octopi.get_status()
            if self.job is not None:
                await self.handle_job()

    async def handle_job(self) -> None:
        if self.job.has_paused():
            try:
                on_filament_empty_command(
                    telegram_client=self.telegram, job=self.job, octopi=self.octopi)
            except Exception as error:  
                logger.error_message(error)
            await self.send_state(prefix='Job paused, probably the filament is empty.\n\n')
        if self.job.has_quarter_achieved():
            try:
                pre_message_command(
                    telegram_client=self.telegram, job=self.job, octopi=self.octopi)
            except Exception as error:
                logger.error_message(error)
            await self.send_state()
            try:
                post_message_command(
                    telegram_client=self.telegram, job=self.job, octopi=self.octopi)
            except Exception as error:
                logger.error_message(error)
            if self.job.has_finished():
                try:
                    post_finished_command(
                        telegram_client=self.telegram, job=self.job, octopi=self.octopi)
                except Exception as error:
                    logger.error_message(error)

if __name__ == '__main__':
    runtime = Runtime()
    asyncio.run(runtime.main())
