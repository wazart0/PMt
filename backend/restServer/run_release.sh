#!/bin/bash

printf '\n\nInitialize DB (migration):\n'
python3 manage.py makemigrations
python3 manage.py migrate

printf '\n\nInitialize DB (insert data):\n'
python3 ./manage.py loaddata 'db.json'

printf '\n\nStart server:\n'
python3 ./manage.py runserver --noreload 0.0.0.0:8000
