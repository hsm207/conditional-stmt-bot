FROM rasa/rasa:2.8.15-full


USER root

RUN pip install black \
    ipykernel \
    jupyterlab \
    pandas

RUN apt update && \
    apt install -y git \
        make \
        wget