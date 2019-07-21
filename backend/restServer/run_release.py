import subprocess

subprocess.call(["python3", "manage.py", "makemigrations"])
subprocess.call(["python3", "manage.py", "migrate"])

subprocess.call(["python3", "./manage.py", "loaddata", "db.json"])

subprocess.call(["python3", "./manage.py", "runserver", "--noreload", "0.0.0.0:8000"])