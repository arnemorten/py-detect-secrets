FROM ubuntu:latest
ADD . /app
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
RUN pip3 install --target=/app requests detect-secrets prettyprint pygithub cffi

CMD ["/app/main.py"]
