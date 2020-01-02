FROM python:latest

RUN pip install pika

ENV PYTHONUNBUFFERED=1

COPY server.py /server/

WORKDIR /server/