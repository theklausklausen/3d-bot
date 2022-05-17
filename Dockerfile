FROM --platform=$BUILDPLATFORM python:alpine
RUN mkdir /app
WORKDIR /app
COPY 3D-Bot.py .
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "python3", "3D-Bot.py"]
