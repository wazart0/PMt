FROM python:3.9.0-buster

WORKDIR /usr/src/app

COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "0", "wsgi:app"]