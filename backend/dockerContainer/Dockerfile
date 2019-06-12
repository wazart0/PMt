FROM python:3
WORKDIR /usr/src/app


COPY ./dockerContainer/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./restServer/ ./
RUN python3 manage.py migrate
RUN python3 ./manage.py loaddata 'db.json'

EXPOSE 8000
CMD [ "python3", "./manage.py", "runserver", "0.0.0.0:8000" ]
