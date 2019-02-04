FROM python:3.7.2-alpine3.8

RUN mkdir /build
ADD requirements.txt /build

RUN apk add  --no-cache --update gcc g++ openblas-dev && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip install -r /build/requirements.txt && \
    rm -rf build