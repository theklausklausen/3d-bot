FROM --platform=$BUILDPLATFORM python:3.7-alpine
RUN mkdir /app
WORKDIR /app
COPY 3D-Bot.py .
RUN pip3 install --requirement requirements.txt
CMD [ "python3", "3D-Bot.py"]
