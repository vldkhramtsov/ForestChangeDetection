FROM nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04

RUN apt-get update && apt-get install -y python3-pip
RUN mkdir /sentinel
WORKDIR /sentinel

# Install dependecies for open-cv:
RUN apt-get update
RUN apt-get install -y libsm6 libxext6 libxrender-dev

# Install packages:
RUN python3 --version
RUN pip3 install --upgrade pip
COPY requirements.txt /sentinel
RUN pip3 install -r requirements.txt

# Install GDAL:
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:ubuntugis/ppa && apt-get update
RUN apt-get update
RUN apt-get install -y gdal-bin libgdal-dev python-gdal python3-gdal
RUN CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN C_INCLUDE_PATH=/usr/include/gdal
RUN pip3 install GDAL

ADD . /sentinel/

# Check GPU availability:
# RUN python3 -c "import tensorflow as tf; print(tf.__version__); print(tf.config.list_physical_devices('GPU'))"
# RUN python3 -c "import keras; print(keras.__version__)"
