FROM python:3.7
MAINTAINER peepee "ppark9553@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
COPY . /app
WORKDIR /app
EXPOSE 8000
RUN pip3 install -r requirements.txt