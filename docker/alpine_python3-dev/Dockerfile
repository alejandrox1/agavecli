FROM python:3.6.6-alpine3.7
MAINTAINER alejandrox1

RUN apk --update add --no-cache git make

ADD agavecli .

run make install

ENTRYPOINT ["agavecli"]
