FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

ENV ALKS_SERVER='https://alks.coxautoinc.com/rest'
ENV ALKS_USERID='jleopold'

EXPOSE 8000

RUN apt-get update && \
  apt-get -y install git autoconf automake libtool python3.7-dev python3-tk jq awscli python3-pip curl && \
  curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
  apt-get -y install nodejs && \
  npm install -g alks && \
  git clone https://github.com/duo-labs/cloudmapper.git && \
  cd cloudmapper/ && \
  python3 -m pip install --user pipenv && \
  ~/.local/bin/pipenv install --deploy --skip-lock

WORKDIR cloudmapper
#COPY scripts/* scripts/

#CMD ~/.local/bin/pipenv run bashdock
#CMD ~/.local/bin/pipenv shell
#CMD ~/.local/bin/pipenv run ./scripts/alks_generate_config_file.pl
#RUN pipenv shell

RUN bash