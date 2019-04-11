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
		linux-headers

ADD https://raw.githubusercontent.com/davido/bazel-alpine-package/master/david@ostrovsky.org-5a0369d6.rsa.pub \
    /etc/apk/keys/david@ostrovsky.org-5a0369d6.rsa.pub
ADD https://github.com/davido/bazel-alpine-package/releases/download/0.22.0/bazel-0.22.0-r0.apk \
    /tmp/bazel-0.22.0-r0.apk

RUN apk add /tmp/bazel-0.22.0-r0.apk

ADD project.tar.gz /app

WORKDIR /app/project

RUN rm -f .bazelrc && \
    cd fetch_teams/oef-core && mkdir build && cd build && cmake .. && make -j16 && cd /app/project && \
    bazel build network_oef/experimental/python:node --force_python=PY3 && \
    bazel build netwrok_oef/experimental/python/demo:demo_director --force_python=PY3 && \
    cp certificates/src/makefiles/oef-search/oef-search.pem /build/server.pem  && \
    cp -Lr bazel-bin /build && \
    cp network_oef/experimental/sh/oef.sh /build/

FROM qati/python3alpine_nlp

WORKDIR /app

COPY --from=builder /build/bazel-bin/network_oef/experimental/python /app/
COPY --from=builder /build/server.pem /app/
COPY --from=builder /build/oef.sh /app/
COPY --from=builder /app/project/cpp-sdk/experimental/resources /app/cpp-sdk/experimental/resources
COPY --from=builder /app/project/ai_search_engine/src/resources/ /app/ai_search_engine/src/resources

RUN apk add protobuf && \
    pip3 install colorlog && \
    chmod +x /app/oef.sh

ENTRYPOINT ["/bin/sh", "/app/oef.sh"]