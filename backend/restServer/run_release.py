import subprocess

print('\n\nInitialize DB (migration):\n')
subprocess.call(["python3", "manage.py", "makemigrations", "ums", "jobs"])
subprocess.call(["python3", "manage.py", "makemigrations"])
subprocess.call(["python3", "manage.py", "migrate"])

print('\n\nInitialize DB (insert data):\n')
print('Inserting global admin...')
subprocess.call(["python3", "./manage.py", "shell", "<", "./initialize/insertAdmin.py"])
# subprocess.call(["python3", "./manage.py", "loaddata", "db.json"])

print('\n\nStart server:\n')
subprocess.call(["python3", "./manage.py", "runserver", "--noreload", "0.0.0.0:8000"])