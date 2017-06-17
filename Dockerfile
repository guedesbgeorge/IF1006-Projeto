FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y python
RUN apt-get install -y python-pip
RUN apt-get install -y curl
RUN apt-get clean all

RUN pip install flask
RUN pip install docker
RUN pip install PyGithub
RUN pip install pyyaml

RUN mkdir /build
COPY core /build

WORKDIR /build

ENV FLASK_APP /build/handler.py
ENV WEB_HOOK_ROUTE http://6ebb253c.ngrok.io

EXPOSE 5000

CMD flask run -h 0.0.0.0 -p 5000
