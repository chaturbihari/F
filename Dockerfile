FROM FROM python:3.10.8-slim-bullseye

RUN apt update && apt upgrade -y && \
    apt install -y git dos2unix

COPY requirements.txt /requirements.txt
RUN pip3 install --upgrade pip && pip3 install --upgrade -r /requirements.txt

RUN mkdir /NewAuto
WORKDIR /NewAuto

COPY . /NewAuto

RUN dos2unix start.sh && chmod +x start.sh

CMD ["./start.sh"]
