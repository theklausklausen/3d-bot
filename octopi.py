import os
import requests
import logging

from logger import Logger
from job import Job
from errors import *


class OctoPi():
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = Logger(debug=debug)
        self.host = os.environ.get(f'OCTOPI_URL', 'http://octoprint.local')
        self.job_url = self.host + '/api/job'
        self.printhead_url = self.host + '/api/printer/printhead'
        self.shutdown_url = self.host + '/api/system/commands/core/shutdown'
        self.printer_state_url = self.host + '/api/printer'
        self.image_url = self.host + '/webcam/?action=snapshot'
        self.token = {
            'Authorization': 'Bearer {token}'.format(token=os.environ.get(f'OCTOPI_KEY', 'abcdefghijklmnopqrstuvwxyz'))}
        if not debug:
            logging.getLogger(f'requests').setLevel(logging.INFO)
            logging.getLogger(f'urllib3').setLevel(logging.INFO)
        self.bed_temp_max = os.environ.get(
            f'OCTOPI_BED_TEMP_MAX', default=None)
        if (self.bed_temp_max is not None):
            try:
                self.bed_temp_max = int(self.bed_temp_max)
            except:
                self.logger.error_message(
                    f'{__name__} OCTOPI_BED_TEMP_MAX is not a valid integer')
        self.tool_temp_max = os.environ.get(
            'OCTOPI_TOOL_TEMP_MAX', default=None)
        if (self.tool_temp_max is not None):
            try:
                self.tool_temp_max = int(self.tool_temp_max)
            except:
                self.logger.error_message(
                    f'{__name__} OCTOPI_TOOL_TEMP_MAX is not a valid integer')

    def temp_is_ok(self) -> bool:
        if (isinstance(self.bed_temp_max, int) or isinstance(self.tool_temp_max, int)):
            response = None
            try:
                response = requests.get(
                    self.printer_state_url, headers=self.token, timeout=5)
            except Exception as error:
                self.logger.error_message(
                    f'{HOST_UNREACHABLE}: failed requesting {self.printer_state_url}')
            self.logger.info_message(f'{__name__} request succeeded')
            if response is None:
                return None
            if response.status_code != 200:
                self.logger.error_message(
                    f'failed to request job state with status code {response.status_code}\n{response}')
            response = response.json()
            if response.get(f'error') is not None:
                error = response.get(f'error')
                self.logger.error_message(
                    f'{__name__} failed to get status with error \"{error}\"')
                return None
            if (response.get(f'temperature') is None):
                self.logger.error_message(
                    f'{__name__} could not determine temperatures, assuming all fine')
                return True
            if (response.get(f'temperature')['bed']['actual'] > self.bed_temp_max):
                self.logger.error_message(f'{__name__} BED IS OVERHEATING!')
                return False
            if (response.get(f'temperature')['tool0']['actual'] > self.tool_temp_max):
                self.logger.error_message(f'{__name__} TOOL IS OVERHEATING!')
                return False
            return True

    def get_status(self) -> Job | None:
        response = None
        self.logger.info_message(f'{__name__} requesting job state')
        try:
            response = requests.get(
                self.job_url, headers=self.token, timeout=5)
        except Exception as error:
            self.logger.warn_message(
                f'{HOST_UNREACHABLE}: failed requesting {self.job_url}')
        if response is None:
            return None
        self.logger.info_message(f'{__name__} request succeeded')
        if response.status_code != 200:
            self.logger.error_message(
                f'failed to request job state with status code {response.status_code}\n{response}')
            return None
        response = response.json()
        if response.get(f'error') is not None:
            error = response.get(f'error')
            self.logger.error_message(
                f'{__name__} failed to get status with error \"{error}\"')
            return None

        estimated_print_time = response.get(f'job')['estimatedPrintTime']
        file = response.get(f'job')['file']['name'].replace(
            '.gcode', '') if response.get(f'job')['file']['name'] else None
        completion = response.get(f'progress')['completion']
        print_time_left = response.get(f'progress')['printTimeLeft']
        print_time = response.get(f'progress')['printTime']
        state = response.get(f'state')
        filament = 0
        if (not not response.get(f'job')['filament']):
            filament = response.get(f'job')[
                'filament']['tool0']['length'] if 'tool0' in response.get(f'job')['filament'] else 0

        self.logger.info_message(
            f'estimated print time: {estimated_print_time} | file: {file} | completion: {completion} | print time left: {print_time_left} | print time: {print_time} | state: {state} | filament: {filament}'
        )

        job = Job(
            estimated_print_time=estimated_print_time,
            file=file,
            completion=completion,
            print_time_left=print_time_left,
            print_time=print_time,
            state=state,
            filament=filament,
            debug=self.debug
        )
        return job

    def get_image(self) -> None:
        response = None
        self.logger.info_message(f'{__name__} requesting image')
        try:
            response = requests.get(self.image_url, stream=True)
        except:
            self.logger.error_message(
                f'failed to request job state, host probably unreachable')
            return None
        self.logger.info_message(f'{__name__} request succeeded')
        if response.status_code != 200:
            self.logger.error_message(
                f'failed to request job state with status code {response.status_code}')
            return None
        return response.raw
