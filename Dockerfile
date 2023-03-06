# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG USER=bot
WORKDIR /app
COPY . /app/
RUN useradd $USER && \
    chown $USER:$USER /app && \
    pip install --upgrade pip && \
    pip install -r requirements.txt
USER $USER
ENTRYPOINT [ "python3", "3d-bot.py"]