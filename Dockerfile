FROM python:3.10-slim

RUN mkdir /app
WORKDIR /app

COPY . /app
RUN mkdir /app/voices
RUN mkdir /app/voice_replies

RUN pip install -r requirements.txt
ENTRYPOINT python main.py