FROM python:3.7-alpine
RUN mkdir /app
WORKDIR /app
COPY 3D-Bot.py .
RUN pip3 install paho-mqtt
CMD [ "python3", "3D-Bot.py"]
