FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y curl
run apt-get install -y ssh
RUN apt-get clean all

# Google Cloud SDK
RUN apt-get update && apt-get install -qqy curl gcc python-dev python-setuptools apt-transport-https lsb-release  && \
    easy_install -U pip && \
    pip install -U crcmod && \
    export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb https://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    apt-get -y remove gcc python-dev python-setuptools && \
    rm -rf /var/lib/apt/lists/* && \    
    gcloud config set core/disable_usage_reporting true && \
    gcloud config set component_manager/disable_update_check true && \
    gcloud config set metrics/environment github_docker_image
VOLUME ["/root/.config"]

RUN apt-get update
RUN apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
RUN apt-key fingerprint 0EBFCD88
RUN add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
RUN apt-get update
RUN apt-get install -y docker-ce


RUN pip3 install flask
RUN pip3 install docker
RUN pip3 install PyGithub
RUN pip3 install pyyaml

RUN eval "$(ssh-agent -s)"

RUN mkdir /build
COPY core /build

WORKDIR /build

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV FLASK_APP /build/handler.py
ENV WEB_HOOK_HOST http://23.251.151.44:5000
    
RUN usermod -aG docker $(whoami)

EXPOSE 443
EXPOSE 5000

CMD flask run --host=0.0.0.0 --port=5000
