FROM python:3.7.2-alpine3.8 AS builder

RUN mkdir -p /app && mkdir /build && \
    apk add \
		openssl \
		g++ \
		make \
		cmake \
		git \
		nss \
		protobuf \
		protobuf-dev \
		linux-headers \
		python3-dev

ADD https://raw.githubusercontent.com/davido/bazel-alpine-package/master/david@ostrovsky.org-5a0369d6.rsa.pub \
    /etc/apk/keys/david@ostrovsky.org-5a0369d6.rsa.pub
ADD https://github.com/davido/bazel-alpine-package/releases/download/0.22.0/bazel-0.22.0-r0.apk \
    /tmp/bazel-0.22.0-r0.apk

RUN apk add /tmp/bazel-0.22.0-r0.apk