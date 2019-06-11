FROM python:3
WORKDIR /usr/src/app


COPY ./dockerContainer/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./restServer/ ./
RUN python3 manage.py migrate
# RUN python3 ./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('user1', 'user1@example.com', 'user1')"
# RUN python3 ./manage.py loaddata 'dump.json'

EXPOSE 8000
CMD [ "python3", "./manage.py", "runserver", "0.0.0.0:8000" ]
