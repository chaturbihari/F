FROM python:3.10.8-slim-buster  

RUN apt update && apt upgrade -y && \
    apt install -y git dos2unix  

COPY requirements.txt /requirements.txt 
RUN pip3 install -U pip && pip3 install -U -r /requirements.txt  

RUN mkdir /NewAuto  
WORKDIR /NewAuto 

# ✅ Copy all files into container
COPY . /NewAuto

# ✅ Fix line endings of start.sh inside the new directory
RUN dos2unix start.sh && chmod +x start.sh  

CMD ["/bin/bash", "start.sh"]
