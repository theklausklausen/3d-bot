import os
import time
import paho.mqtt.client as mqtt

from logger import Logger


class MQTT:
    def __init__(self, debug: bool = False):
        self.telegram_api_key = os.environ.get('TELEGRAM_API_KEY', 'token')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', 'chat_id')
        self.host = os.environ.get('MQTT_HOST', 'test.mosquitto.org')
        try:
            self.port = int(os.environ.get('MQTT_PORT', '1883'))
        except:
            raise EnvironmentError('MQTT_PORT must be a digit')
        self.user = os.environ.get('MQTT_USER', 'user')
        self.password = os.environ.get('MQTT_PASSWORD', 'password')
        self.id = os.environ.get('MQTT_ID', '3d-bot')
        self.lamp_topic = os.environ.get('MQTT_LAMP_TOPIC', '/command/topic')
        self.lamp_on = os.environ.get('MQTT_LAMP_ON', 'on')
        self.lamp_off = os.environ.get('MQTT_LAMP_OFF', 'off')
        self.verify_ssl_certificate = os.environ.get(
            'MQTT_SSL_VERIFICATION', False)
        self.logger = Logger(debug=debug)

        self.client = self.initClient()
        self.connectClient()
        self.client.on_connect = self.on_connect

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
        self.logger.debug_message('usiing user {user}, id {id}, password {password}'.format(
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
