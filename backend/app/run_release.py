import subprocess
import os

print('\n\nInitialize DB (migration):\n')
os.system('python3 manage.py makemigrations')
os.system('python3 manage.py migrate')
# subprocess.run(["python3", "manage.py", "makemigrations"])
# subprocess.run(["python3", "manage.py", "migrate"])

print('\n\nInitialize DB (insert data):\n')
os.system('python3 ./manage.py shell < ./initialize/insertAdmin.py')
os.system('python3 ./manage.py shell < ./initialize/initializeModuleUMS.py')
os.system('python3 ./manage.py shell < ./initialize/initializeModuleJobs.py')
# subprocess.run(["python3", "./manage.py", "runscript", "./initialize/insertAdmin.py"])
# subprocess.run(["python3", "./manage.py", "shell", "<", "./initialize/initializeModuleUMS.py"])
# subprocess.run(["python3", "./manage.py", "shell", "<", "./initialize/initializeModuleJobs.py"])

print('\n\nStart server:\n')
os.system('python3 ./manage.py runserver --noreload 0.0.0.0:8000')
# subprocess.run(["python3", "./manage.py", "runserver", "--noreload", "0.0.0.0:8000"])