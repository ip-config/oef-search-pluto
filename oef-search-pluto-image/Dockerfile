FROM ubuntu:18.04

USER root

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y clang && \
    apt-get install -y gcc && \
    apt-get install -y g++ && \
    apt-get install -y make

ENV CC=/usr/bin/gcc
ENV CXX=/usr/bin/g++

RUN apt-get install -y python3-pip python3-dev

RUN apt-get install protobuf-compiler -y && \
    apt-get install libprotobuf-dev -y && \
    apt-get install python-protobuf -y


RUN apt-get install -y pkg-config zip g++ zlib1g-dev unzip python wget
RUN wget https://github.com/bazelbuild/bazel/releases/download/0.23.0/bazel-0.23.0-installer-linux-x86_64.sh && \
    chmod +x bazel-0.23.0-installer-linux-x86_64.sh && \
    ./bazel-0.23.0-installer-linux-x86_64.sh

WORKDIR /source
COPY . /source

RUN bazel build fetch_teams/bottle

#RUN rm -Rf build &&\
#    mkdir build &&\
#    cd build &&\
#    cmake .. &&\
#    make -j4

#RUN cp -r ./build/apps /apps

EXPOSE 3334
CMD ["/bin/bash"]
