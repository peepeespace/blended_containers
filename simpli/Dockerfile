FROM python:3.7
MAINTAINER peepee "ppark9553@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD celery -A simpli worker --loglevel=INFO -n simpli-worker-1@%h