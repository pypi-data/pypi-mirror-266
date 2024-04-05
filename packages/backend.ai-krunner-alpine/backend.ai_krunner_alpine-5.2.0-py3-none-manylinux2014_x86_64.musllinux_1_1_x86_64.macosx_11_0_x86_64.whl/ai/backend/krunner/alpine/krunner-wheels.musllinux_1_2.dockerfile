FROM python:3.12.2-alpine

RUN apk add \
	build-base \
	ca-certificates

COPY requirements.txt /root/

RUN set -ex \
    && cd /root \
    && pip wheel -w ./wheels -r requirements.txt


# vim: ft=dockerfile
