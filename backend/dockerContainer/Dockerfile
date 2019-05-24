# FROM python:3
# WORKDIR /usr/src/app

FROM ubuntu
WORKDIR /root

RUN apt-get --assume-yes update
RUN apt-get --assume-yes install python3
RUN apt-get --assume-yes install python3-pip

COPY ./dockerContainer/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./djangoRESTframework/ ./
RUN ls -la
RUN python3 manage.py migrate

EXPOSE 8000
CMD [ "python3", "./manage.py", "runserver" ]
