FROM python:3.7-slim as cloudmapper

LABEL Project="https://github.com/duo-labs/cloudmapper"
ADD VERSION .

EXPOSE 8000
WORKDIR /opt/cloudmapper

RUN apt-get update -y
RUN apt-get -y install build-essential git autoconf automake libtool python3.7-dev python3-tk jq awscli python3-pip curl netcat
RUN apt-get install -y bash

RUN git clone https://github.com/duo-labs/cloudmapper.git /opt/cloudmapper

RUN mkdir /opt/cloudmapper/port_check
COPY files/* /opt/cloudmapper/
COPY files/port_check/ /opt/cloudmapper/port_check/
RUN chmod +x /opt/cloudmapper/cloudmapper.sh

#RUN mkdir /opt/cloudmapper/port_check
#COPY files/port_check/* /opt/cloudmapper/port_check/

RUN pip install pipenv
RUN pipenv install --skip-lock
#RUN pipenv shell

RUN bash
