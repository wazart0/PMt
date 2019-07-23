#!/bin/sh

printf '\n\nInitialize DB (migration):\n'
python3 manage.py makemigrations ums jobs
python3 manage.py makemigrations
python3 manage.py migrate

printf '\n\nInitialize DB (insert data):\n'
printf 'Inserting global admin...'
python3 ./manage.py shell < ./insertAdmin.py
# python3 ./manage.py loaddata 'db.json'

printf '\n\nStart server:\n'
python3 ./manage.py runserver_plus --print-sql 0.0.0.0:8000
