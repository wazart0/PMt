import requests

print('Creating example users...')

def userAPIurl(userID):
    return 'http://localhost:8000/up/' + str(userID) + '/user/'

r = requests.get(url = userAPIurl(1))

if r.status_code != 200:
    exit()

data = r.json()

if data['count'] > 1:
    print('\nUsers are already exist.\n')
    exit()

users = [
        {
            "email": "awaz@gmail.com",
            "password": "string",
            "creator_id": "1"
        },
        {
            "email": "kinoko@gmail.com",
            "password": "string",
            "creator_id": "1"
        },
        {
            "email": "ilu1@gmail.com",
            "password": "string",
            "creator_id": "1"
        },
        {
            "email": "wazartur@gmail.com",
            "password": "string",
            "creator_id": "2"
        },
        {
            "email": "trol@wp.pl",
            "password": "string",
            "creator_id": "2"
        },
        {
            "email": "ktostam@ijk.uk",
            "password": "string",
            "creator_id": "5"
        },
        {
            "email": "xyz@fg.lk",
            "password": "string",
            "creator_id": "3"
        },
        {
            "email": "adrian@gmai.com",
            "password": "string",
            "creator_id": "4"
        },
        {
            "email": "string@string.com",
            "password": "string",
            "creator_id": "8"
        }
    ]

for i in users:
    r = requests.post(url = userAPIurl(i['creator_id']), data = i)
    if r.status_code != 201:
        raise('\nERROR: User init failed, cannot create user: ' + i['email'] + '.\n')

print('\nUsers initialized properly.\n')
