import asyncio
import os
import time
import datetime
from dotenv import load_dotenv

from octopi import OctoPi
from job import Job
from logger import Logger
from telegram_client import Telegram


async def main():
    load_dotenv()

    debug = os.environ.get('DEBUG', default=False)
    Logger(debug=debug).info_message('starting up...')
    sleep_time = int(os.environ.get('SLEEP_TIME', '5'))
    telegram = Telegram(debug=debug)
    octopi = OctoPi(debug=debug)

    while True:
        time.sleep(sleep_time)
        job = octopi.get_status()
        if not job:
            continue
        if job.has_quarter_achieved():
            message = 'The job of {file} has reached {completion:.2f}% of completion.\nETA: {eta} hrs\n{link}'.format(
                file=job.file, completion=job.progress['completion'], eta=str(datetime.timedelta(seconds=job.progress['print_time_left'])), link=octopi.host)
            image = octopi.get_image()
            await telegram.send_image(message, image)

if __name__ == "__main__":
    asyncio.run(main())
