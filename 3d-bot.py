import asyncio
import os
import time
import datetime
import logging
from dotenv import load_dotenv
import sys
import subprocess

from octopi import OctoPi
from job import Job
from logger import Logger
from telegram_client import Telegram

logger = telegram = octopi = job = None


class Runtime():
    debug = os.environ.get('DEBUG', default=False) == 'True'
    logger = Logger(debug=debug)
    telegram = Telegram(debug=debug)
    octopi = OctoPi(debug=debug)
    job = None
    if not debug:
        logging.getLogger('asyncio').setLevel(logging.INFO)

    module = import_path = script_path = None

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
            except:
                logger.error_message(
                    'CUSTOM_SCRIPT_PATH has to be like "/path/to/file.py"')
        else:
            raise ImportError('{script} not founf'.format(script=script_path))

    if module:
        sys.path.insert(1, import_path)

        # pre message command
        try:
            preMessageCommand = getattr(__import__(
                module, fromlist=['preMessageCommand']), 'preMessageCommand')
            logger.info_message(message='found \"preMessageCommand\" function')
        except AttributeError:
            logger.info_message(
                message='no \"preMessageCommand\" function found, using default definition')

            def preMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
                print('*** pre message command ***')

            pass

        # post message command
        try:
            postMessageCommand = getattr(__import__(
                module, fromlist=['postMessageCommand']), 'postMessageCommand')
            logger.info_message(
                message='found \"postMessageCommand\" function')
        except AttributeError:
            logger.info_message(
                message='no \"postMessageCommand\" function found, using default definition')

            def postMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
                print('*** post message command ***')

            pass

        # post finished command
        try:
            postFinishedCommand = getattr(__import__(
                module, fromlist=['postFinishedCommand']), 'postFinishedCommand')
            logger.info_message(
                message='found \"postFinishedCommand\" function')
        except AttributeError:
            logger.info_message(
                message='no \"postFinishedCommand\" function found, using default definition')

            def postFinishedCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
                print('*** post finished command ***')

            pass

        # post filament empty command
        try:
            onFilamentEmptyCommand = getattr(__import__(
                module, fromlist=['onFilamentEmptyCommand']), 'onFilamentEmptyCommand')
            logger.info_message(
                message='found \"onFilamentEmptyCommand\" function')
        except AttributeError:
            logger.info_message(
                message='no \"onFilamentEmptyCommand\" function found, using default definition')

            def onFilamentEmptyCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
                print('*** post on filament empty command ***')

            pass
    else:
        def preMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** pre message command ***')

        def postMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** post message command ***')

        def postFinishedCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** post finished command ***')

        def onFilamentEmptyCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
            print('*** post on filament empty command ***')

    async def sendState(self, prefix: str = ''):
        self.logger.info_message('sending state')
        message = '{prefix}The job of {file} has reached {completion:.2f}% of completion.\nETA: {eta} hrs\n{link}'.format(
            prefix=prefix,
            file=self.job.file,
            completion=self.job.progress['completion'],
            eta=str(datetime.timedelta(
                seconds=self.job.progress['print_time_left'])),
            link=self.octopi.host
        )
        image = self.octopi.get_image()
        await self.telegram.send_image(message, image)

    async def main(self):
        load_dotenv()

        self.logger.info_message('starting up...')
        sleep_time = int(os.environ.get('SLEEP_TIME', '5'))

        while True:
            time.sleep(sleep_time)
            self.job = self.octopi.get_status()
            if isinstance(self.job, Job):
                if self.job.has_paused():
                    self.onFilamentEmptyCommand(
                        telegram_client=self.telegram, job=job, octopi=self.octopi)
                    await self.sendState(prefix='Job paused, probably the filament is empty.\n\n')
                if self.job.has_quarter_achieved():
                    try:
                        self.preMessageCommand(
                            telegram_client=self.telegram, job=job, octopi=self.octopi)
                    except Exception as error:
                        self.logger.error_message(error)
                    await self.sendState()
                    try:
                        self.postMessageCommand(
                            telegram_client=self.telegram, job=job, octopi=self.octopi)
                    except Exception as error:
                        self.logger.error_message(error)
                    if self.job.has_finished():
                        self.postFinishedCommand(
                            telegram_client=self.telegram, job=job, octopi=self.octopi)


if __name__ == '__main__':
    runtime = Runtime()
    asyncio.run(runtime.main())
