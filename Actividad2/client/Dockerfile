FROM python:latest

RUN pip install pika

ENV PYTHONUNBUFFERED=1

COPY client.py /client/

WORKDIR /client/   