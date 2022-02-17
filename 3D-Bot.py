import os
import time
from PIL import Image
import requests
from io import BytesIO
import datetime
from paho.mqtt import client as mqtt_client

from dotenv import load_dotenv

load_dotenv()

octopi_job_url = os.environ.get('OCTOPI_URL', 'http://octoprint.local') + '/api/job'
octopi_printhead_url = os.environ.get('OCTOPI_URL', 'http://octoprint.local') + '/api/printer/printhead'
octopi_shutdown_url = os.environ.get('OCTOPI_URL', 'http://octoprint.local') + '/api/system/commands/core/shutdown'
octopi_image_url = os.environ.get('OCTOPI_URL', 'http://octoprint.local') + '/webcam/?action=snapshot'
token = {"x-api-key" : os.environ.get('OCTOPI_KEY', 'abcdefghijklmnopqrstuvwxyz')}
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '1234567890')
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '1234567890')
telegram_text_url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&text='
telegram_image_url = 'https://api.telegram.org/bot' + bot_token + '/sendPhoto?' + 'caption='
mqtt_host = os.environ.get('MQTT_HOST', '127.0.0.1')
mqtt_port = os.environ.get('MQTT_PORT', 1883)
mqtt_user = os.environ.get('MQTT_USER', 'user')
mqtt_password = os.environ.get('MQTT_PASSWORD', 'password')
lamp_topic = os.environ.get('MQTT_LAMP_TOPIC', '/lamp/topic')
lamp_topic = os.environ.get('MQTT_LAMP_TOPIC', '/lamp/topic')
lamp_on_command = topic = os.environ.get('MQTT_LAMP_ON', 'on')
lamp_off_command = os.environ.get('MQTT_LAMP_OFF', 'off')
printer_topic = os.environ.get('MQTT_PRINTER_TOPIC', '/printer/topic')
printer_off_command = os.environ.get('MQTT_PRINTER_OFF', 'off')
octo_topic = os.environ.get('MQTT_OCTO_TOPIC', '/octo/topic')
octo_off_command = os.environ.get('MQTT_OCTO_OFF', 'off')

state = {
    25: True,
    50: True,
    75: True,
    100: True
}

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client('3d-bot')
    client.username_pw_set(mqtt_user, mqtt_password)
    client.on_connect = on_connect
    client.connect(mqtt_host, int(mqtt_port))
    return client

def publish(topic, message, client):
    result = client.publish(topic, message)
    status = result[0]
    if status == 0:
        print(f"MQTT :: Send `{message}` to topic `{topic}`")
    else:
        print(f"MQTT :: Failed to send message to topic {topic}")

def resetState():
    setState(25, True)
    setState(50, True)
    setState(75, True)
    setState(100, True)

def handleConnectionError(message, sendMessageActivated = True):
    print('failed: ' + message)
    if sendMessageActivated:
        sendMessage('MQTT :: failed: ' + message)

def sendMessage(message):
    url = telegram_text_url + message
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(str(datetime.datetime.now()) + ' sent: chadID:' + chat_id + ' message: ' + message)
        else:
            print(response.status_code, response.reason, response.content)
    except requests.ConnectionError:
        handleConnectionError(url, False)

def sendImage(name, percentage, client, print_time_left = ''):
    caption = 'Print ' + name + ' is ' + str(round(percentage, 2)) + '% done!'
    url = telegram_image_url + caption + ' ' + print_time_left
    photo = {'photo': getImage(name, client)}
    data = {'chat_id' : chat_id}
    try:
        response = requests.post(url, files=photo, data=data)
        if response.status_code == 200:
            print(str(datetime.datetime.now()) + ' sent: chadID:' + chat_id + ' image:' + name + '.img completion:' + str(round(percentage, 2)) + '%')
        else:
            print(response.status_code, response.reason, response.content)
            sendMessage('Attention: Sending Image went wrong')
    except requests.ConnectionError:
        handleConnectionError(url)

def getImage(name, client):
    switchRelay(lamp_topic, lamp_on_command, client)
    try:
        response = requests.get(octopi_image_url)
        if response.status_code == 200:
            print(str(datetime.datetime.now()) + ' get: url:' + octopi_image_url)
        else:
            print(response.status_code, response.reason, response.content)
            sendMessage('Attention: getting OctoPi Image went wrong')
    except requests.ConnectionError:
        handleConnectionError(octopi_image_url)
    photo = BytesIO(response.content)
    photo.name = name + '.png'
    time.sleep(10.0)
    switchRelay(lamp_topic, lamp_off_command, client)
    return photo

def switchRelay(topic, state, client):
    print('mqtt ' + topic + '/' + state)
    publish(topic, state, client)
    time.sleep(3.0)

def setState(stateNumber, stateValue):
    state[stateNumber] = stateValue

def devidePercentage(name, percentage, print_time_left, client):
    if percentage >= 100 and state[100]:
        try:
            response = requests.post(octopi_printhead_url, headers=token, data={'absolute':False,'y':-150,'command':'jog'})
            if response.status_code == 200:
                print(str(datetime.datetime.now()) + ' sent: url:' + octopi_printhead_url + ' command:center plate')
            else:
                print(response.status_code, response.reason, response.content)
        except requests.ConnectionError:
            handleConnectionError(octopi_printhead_url)
        time.sleep(5.0)
        sendImage(name, percentage, client)
        setState(100, False)
        time.sleep(30.0)
        try:
            response = requests.post(octopi_shutdown_url, headers=token)
            if response.status_code == 200:
                print(str(datetime.datetime.now()) + ' sent: url:' + octopi_shutdown_url + ' command:shutdown')
            else:
                print(response.status_code, response.reason, response.content)
        except requests.ConnectionError:
            handleConnectionError(octopi_shutdown_url)
        switchRelay(printer_topic, printer_off_command, client)
        time.sleep(60.0)
        switchRelay(octo_topic, octo_off_command, client)
    if percentage <= 10:
        resetState()
    if percentage >= 25 and percentage < 50 and state[25]:
        setState(25, False)
        sendImage(name, percentage, client, print_time_left)    
    if percentage >= 50 and percentage < 75 and state[50]:
        setState(50, False)
        sendImage(name, percentage, client, print_time_left)    
    if percentage >= 75 and percentage < 100 and state[75]:
        setState(75, False)
        sendImage(name, percentage, client, print_time_left)    

def mqtt_reconnect():
    client = connect_mqtt()
    client.loop_start()
    return client

def main():
    resetState()
    sendMessage('Starting Bot 3DB')
    client = mqtt_reconnect()
    while True:
        response = None
        try:
            response = requests.get(octopi_job_url, headers=token)
            if response.status_code == 200:
                print(str(datetime.datetime.now()) + ' get: url:' + octopi_job_url)
            else:
                print(response.status_code, response.reason, response.content)
                sendMessage('Attention: getting OctoPi Status went wrong')
        except requests.ConnectionError:
            handleConnectionError(octopi_job_url, not state[25])
        minutes = 0
        if bool(response):
            if (response.json()['progress']['printTimeLeft'] != None):
                minutes = int(int(response.json()['progress']['printTimeLeft']) / 60 )
            hour = int(minutes/60)
            minutes = minutes - hour * 60
            print_time_left = str(hour) + ' Hours ' + str(minutes) + ' Minutes remaining'
            name = response.json()['job']['file']['name'] 
            completion = response.json()['progress']['completion'] or 0
            devidePercentage(name, completion, print_time_left, client)
            print(name + ' : ' + str(round(completion, 2)) + '%')
        time.sleep(5.0)

if __name__ == "__main__":
    main()