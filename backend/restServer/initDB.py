import requests


def addUser(json):
    resp = requests.post('http://localhost:8000/users/', json=json)
    if resp.status_code != 201:
        return print('POST /users/ {}'.format(resp.status_code))
    print('Created user. ID: {}'.format(resp.json()["id"]))

u1 = {
  "email": "admin@ad.com",
  "password": "test1",
  "isActive": "true"
}

u2 = {
  "email": "user@us.com",
  "password": "test1",
  "isActive": "true"
}


addUser(u1)
addUser(u2)