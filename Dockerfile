FROM python:3.6

RUN pip install opcua-broker

CMD opcua-broker
