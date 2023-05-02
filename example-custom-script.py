import paho.mqtt.client as mqtt
import time
import os
from octopi import OctoPi
from job import Job
from logger import Logger
from telegram_client import Telegram


def preMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi):
    MQTT().turnOnLight()


def postMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi):
    MQTT().turnOffLight()


class MQTT:

    _instance = None

    def __new__(
        cls,
        debug=False
    ):
        if cls._instance is None:
            cls._instance = super(MQTT, cls).__new__(cls)
            super().__init__(cls)
            cls._instance.host = os.environ.get(
                'MQTT_HOST', 'test.mosquitto.org')
            try:
                cls._instance.port = int(os.environ.get('MQTT_PORT', '1883'))
            except:
                raise EnvironmentError('MQTT_PORT must be a digit')
            cls._instance.user = os.environ.get('MQTT_USER', 'user')
            cls._instance.password = os.environ.get(
                'MQTT_PASSWORD', 'password')
            cls._instance.id = os.environ.get('MQTT_ID', '3d-bot')
            cls._instance.lamp_topic = os.environ.get(
                'MQTT_LAMP_TOPIC', '/command/topic')
            cls._instance.lamp_on = os.environ.get('MQTT_LAMP_ON', 'on')
            cls._instance.lamp_off = os.environ.get('MQTT_LAMP_OFF', 'off')
            cls._instance.verify_ssl_certificate = os.environ.get(
                'MQTT_SSL_VERIFICATION', False)
            cls._instance.logger = Logger(debug=debug)
            cls._instance.logger.debug_message('created new mqtt object')
            cls._instance.client = cls._instance.initClient()
            cls._instance.connectClient()
            cls._instance.client.on_connect = cls._instance.on_connect

        return cls._instance

    def __del__(self):
        self.logger.info_message('deleting mqtt instance')

    def initClient(self):
        self.logger.info_message(
            'creating mqtt-client for {user} - {id}'.format(user=self.user, id=self.id))
        client = mqtt.Client(
            client_id=self.id,
            clean_session=False
        )
        client.username_pw_set(
            self.user,
            self.password
        )
        return client

    def connectClient(self):
        self.logger.info_message('trying to connect to {host}:{port} ...'.format(
            host=self.host, port=self.port))
        self.logger.debug_message('using user {user}, id {id}, password {password}'.format(
            user=self.user,
            id=self.id,
            password=self.password
        ))
        try:
            result = self.client.connect(self.host, self.port)
        except Exception as error:
            self.logger.error_message('failed mqtt connection to {host}:{port} with result {result}'.format(
                host=self.host, port=self.port, result=error))
            return False
        return True

    def on_connect(self, userdata, flags, rc, result):
        self.logger.info_message('successfull mqtt connection to {host}:{port}'.format(
            host=self.host, port=self.port))
        self.logger.debug_message('userdata: {userdata}\nflags: {flags}\nrc: {rc}\nresult: {result}'.format(
            userdata=userdata,
            flags=flags,
            rc=rc,
            result=result
        ))

    def turnOnLight(self):
        self.connectClient()
        self.publishMessage(self.lamp_topic, self.lamp_on)
        time.sleep(5)

    def turnOffLight(self):
        self.connectClient()
        self.publishMessage(self.lamp_topic, self.lamp_off)
        time.sleep(5)

    def publishMessage(self, topic: str, payload: str):
        self.logger.info_message('sending mqtt payload {payload} on {topic}'.format(
            payload=payload, topic=topic))
        self.client.publish(topic=topic, payload=payload)
