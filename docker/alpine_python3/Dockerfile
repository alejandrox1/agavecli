FROM python:3.7.0-alpine3.7
MAINTAINER alejandrox1

RUN apk --update add --no-cache git make && \
    git clone https://github.com/alejandrox1/agavecli && \                          
    cd agavecli && \                                                            
    make install && \
    rm -rf /var/cache/apk/*

WORKDIR /root

ENTRYPOINT ["agavecli"]
