FROM ubuntu:22.04

RUN mkdir /code
WORKDIR /code

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && \
    apt-get -y install bc curl gnupg2 jq less python3 python3-pip unzip wget git && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt