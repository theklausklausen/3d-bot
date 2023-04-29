import os
import requests
import logging

from logger import Logger
from job import Job


class OctoPi():
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = Logger(debug=debug)
        self.host = os.environ.get('OCTOPI_URL', 'http://octoprint.local')
        self.job_url = self.host + '/api/job'
        self.printhead_url = self.host + '/api/printer/printhead'
        self.shutdown_url = self.host + '/api/system/commands/core/shutdown'
        self.image_url = self.host + '/webcam/?action=snapshot'
        self.token = {
            'Authorization': 'Bearer {token}'.format(token=os.environ.get('OCTOPI_KEY', 'abcdefghijklmnopqrstuvwxyz'))}
        if not debug:
            logging.getLogger('requests').setLevel(logging.INFO)
            logging.getLogger('urllib3').setLevel(logging.INFO)

    def get_status(self) -> Job | None:
        response = None
        self.logger.info_message('requesting job state')
        try:
            response = requests.get(
                self.job_url, headers=self.token, timeout=5)
        except:
            self.logger.error_message(
                'failed to request job state, host probably unreachable')
            return None
        self.logger.info_message('request succeeded')
        if response.status_code != 200:
            self.logger.error_message(
                'failed to request job state with status code {code}\n{message}'.format(code=response.status_code, message=response.json()))
            return None
        response = response.json()
        if response.get('error') is not None:
            self.logger.error_message('failed to get status with error \"{error}\"'.format(
                error=response.get('error')))
            return None

        job = Job(
            estimated_print_time=response.get('job')['estimatedPrintTime'],
            file=response.get('job')['file']['name'].replace('.gcode', ''),
            completion=response.get('progress')['completion'],
            print_time_left=response.get('progress')['printTimeLeft'],
            print_time=response.get('progress')['printTime'],
            state=response.get('state'),
            debug=self.debug
        )
        return job

    def get_image(self) -> None:
        response = None
        self.logger.info_message('requesting image')
        try:
            response = requests.get(self.image_url, stream=True)
        except:
            self.logger.error_message(
                'failed to request job state, host probably unreachable')
            return None
        self.logger.info_message('request succeeded')
        if response.status_code != 200:
            self.logger.error_message(
                'failed to request job state with status code {code}'.format(code=response.status_code))
            return None
        return response.raw
