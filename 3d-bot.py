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
from mqtt_client import MQTT

logger = telegram = octopi = job = None


class Runtime():
    debug = os.environ.get('DEBUG', default=False) == 'True'
    logger = Logger(debug=debug)
    telegram = Telegram(debug=debug)
    octopi = OctoPi(debug=debug)
    mqtt = MQTT(debug=debug)
    job = None
    if not debug:
        logging.getLogger('asyncio').setLevel(logging.INFO)

    def preMessageCommand(self):
        self.mqtt.turnOnLight()

    def postMessageCommand(self):
        self.mqtt.turnOffLight()

    async def sendState(self, prefix: str = ''):
        self.preMessageCommand()
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
        self.postMessageCommand()

    async def main(self):
        load_dotenv()

        self.logger.info_message('starting up...')
        sleep_time = int(os.environ.get('SLEEP_TIME', '5'))

        while True:
            time.sleep(sleep_time)
            self.job = self.octopi.get_status()
            if isinstance(self.job, Job):
                if self.job.has_paused():
                    await self.sendState(prefix='Job paused, probably the filament is empty.\n\n')
                if self.job.has_quarter_achieved():
                    await self.sendState()


if __name__ == '__main__':
    runtime = Runtime()
    asyncio.run(runtime.main())
