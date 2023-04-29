import asyncio
import os
import time
import datetime
import logging
from dotenv import load_dotenv

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

    async def sendState(self):
        self.logger.info_message('sending state')
        paused_message = 'Job paused, probably the filament is empty.\n\n' if self.job.has_paused() else ''
        message = '{paused_message}The job of {file} has reached {completion:.2f}% of completion.\nETA: {eta} hrs\n{link}'.format(
            paused_message=paused_message,
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
                if self.job.has_quarter_achieved() or self.job.has_paused():
                    await self.sendState()


if __name__ == '__main__':
    runtime = Runtime()
    asyncio.run(runtime.main())
