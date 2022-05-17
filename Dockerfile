FROM --platform=$BUILDPLATFORM python:alpine
RUN mkdir /app
WORKDIR /app
COPY 3D-Bot.py .
COPY requirements.txt .
RUN pip3 install --requirement requirements.txt
CMD [ "python3", "3D-Bot.py"]
