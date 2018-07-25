FROM debian:stretch as base

WORKDIR /root
RUN apt-get update -y && apt-get install -yq curl && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /src/.*deb && \
    curl -L https://raw.githubusercontent.com/alejandrox1/dev_env/master/local-setup/bashrc \
    -o /root/.bashrc && \
    curl -L https://raw.githubusercontent.com/alejandrox1/dev_env/master/local-setup/bash_prompt \
    -o /root/.bash_prompt


FROM python:3.7.0-stretch

COPY --from=base /root/.bashrc /root/.bashrc
COPY --from=base /root/.bash_prompt /root/.bash_prompt

RUN apt-get update -y && apt-get install -y git bash-completion && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /src/.*deb && \
    pip install pytest

WORKDIR /agavecli
COPY . /agavecli

CMD ["/bin/bash"]
