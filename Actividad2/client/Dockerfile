FROM python:latest

RUN python -m pip install grpcio \
    && python -m pip install grpcio-tools

COPY client.py /client/

WORKDIR /client/   