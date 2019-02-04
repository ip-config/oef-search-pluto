FROM python:3.7.2-alpine3.8 AS builder

RUN mkdir -p /app && mkdir /build && \
    apk add \
		openssl \
		g++

ADD https://raw.githubusercontent.com/davido/bazel-alpine-package/master/david@ostrovsky.org-5a0369d6.rsa.pub \
    /etc/apk/keys/david@ostrovsky.org-5a0369d6.rsa.pub
ADD https://github.com/davido/bazel-alpine-package/releases/download/0.22.0/bazel-0.22.0-r0.apk \
    /tmp/bazel-0.22.0-r0.apk

RUN apk add /tmp/bazel-0.22.0-r0.apk

ADD project.tar.gz /app

WORKDIR /app/oef-search-pluto

RUN rm .bazelrc && \
    bazel build api/src/python:communication_handler --force_python=PY3 && \
    cp testapp/src/resources/ssl/* /build  && \
    cp -Lr bazel-bin /build

FROM qati/python3alpine_nlp

WORKDIR /app

COPY --from=builder /build/bazel-bin/api/src/python/ /app/
COPY --from=builder /build/server.pem /app/

EXPOSE 7500-7501

ENTRYPOINT ["./communication_handler", "7500", "server.pem"]
