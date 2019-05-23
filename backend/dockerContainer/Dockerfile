FROM python:3

WORKDIR /usr/src/app

COPY ./dockerContainer/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./djangoRESTframework/ ./
RUN ls -la
RUN python manage.py migrate

EXPOSE 8000
# RUN python manage.py runserver
CMD [ "python", "./manage.py", "runserver" ]
# CMD [ "ls", "-la" ]
