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

RUN pip3 install colorlog scipy gensim nltk

RUN apt-get install -y pkg-config zip g++ zlib1g-dev unzip python wget
RUN wget https://github.com/bazelbuild/bazel/releases/download/0.23.0/bazel-0.23.0-installer-linux-x86_64.sh && \
    chmod +x bazel-0.23.0-installer-linux-x86_64.sh && \
    ./bazel-0.23.0-installer-linux-x86_64.sh

RUN apt-get install -y git

WORKDIR /source
COPY . /source

# tmp patches
RUN sed -i '/python_path/ s/="[^"][^"]*"/="\/usr\/bin\/python3.6"/' .bazelrc && \
    sed -i '31s/#//' ai_search_engine/src/python/SearchEngine.py
RUN grep -qxF  'daps[-1].wait(daps[-1])' dap_api/experimental/python/RunNetworkDaps.py || \
    echo "daps[-1].wait(daps[-1])" >> dap_api/experimental/python/RunNetworkDaps.py

RUN bazel build dap_api/experimental/python:network_daps pluto_app/src/python:pluto

RUN echo "/source/bazel-bin/dap_api/experimental/python/network_daps" > run_py_pluto.sh && \
    echo "/source/bazel-bin/pluto_app/src/python/pluto --ssl_certificate certificates/src/makefiles/oef-search/oef-search.pem --http_port 7500 --socket_port 7501" >> run_py_pluto.sh && \
    chmod +x run_py_pluto.sh  

EXPOSE 7501
CMD /source/run_py_pluto.sh
