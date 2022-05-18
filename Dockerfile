# syntax=docker/dockerfile:1
FROM python:alpine
RUN mkdir /app
WORKDIR /app
COPY 3D-Bot.py requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "python3", "3D-Bot.py"]
