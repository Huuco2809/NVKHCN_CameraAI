# truonglm.spk@gmail.com - 29 Apr, 2023
# Dockerfile

FROM ubuntu:18.04
LABEL maintainer="truonglm.spk@gmail.com"
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update
RUN apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && apt install -y wget build-essential python3.10 python3.10-dev
RUN wget https://bootstrap.pypa.io/get-pip.py && python3.10 get-pip.py
RUN pip3 install --upgrade pip
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y python3-opencv  # fix for opencv
RUN pip3 install opencv-python

