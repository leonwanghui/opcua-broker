FROM python:3.5

ADD ./opcua-broker /opcua-broker

RUN apt-get update && apt-get install -y python-dev python-pip
RUN pip install cryptography opcua openbrokerapi flask

CMD ["python", "/opcua-broker/service-broker.py", "-u", "opc.tcp://localhost:4840"]
