FROM python:latest

RUN python -m pip install grpcio \
    && python -m pip install grpcio-tools

COPY client.py /client/
COPY chat_pb2.py /client/
COPY chat_pb2_grpc.py /client/

WORKDIR /client/   