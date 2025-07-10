FROM python:3.10.8-slim-buster  

RUN apt update && apt upgrade -y && \
    apt install -y git dos2unix  

# Copy requirements
COPY requirements.txt /requirements.txt 
RUN pip3 install -U pip && pip3 install -U -r /requirements.txt  

# Create and set working directory
RUN mkdir /NewAuto  
WORKDIR /NewAuto 

# Copy your bot files to the container
COPY . /NewAuto

# Make start script executable
RUN dos2unix /start.sh && chmod +x /start.sh  

CMD ["/bin/bash", "/start.sh"]
