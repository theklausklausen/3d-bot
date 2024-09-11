ARG BASE_IMG=repo.kk.int/infra-images/python-base:latest
FROM ${BASE_IMG} AS dev
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG USER=bot
WORKDIR /app
COPY . /app/
RUN addgroup -S -g 1000 $USER && \
    adduser -u 1000 -SHG $USER $USER
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    pip3 install debugpy
USER $USER
CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:3001", "3d-bot.py"]

FROM repo.kk.int/infra-images/python-base:latest AS prod
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG USER=bot
WORKDIR /app
COPY . /app/
RUN addgroup -S -g 1000 $USER && \
    adduser -u 1000 -SHG $USER $USER
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt
USER $USER
CMD ["python3", "3d-bot.py"]