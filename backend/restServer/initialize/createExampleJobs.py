import requests

print('Creating example jobs...')

def jobAPIurl(userID):
    return 'http://localhost:8000/up/' + str(userID) + '/job/'
    
def jobAuthorizationAPIurl(userID, jobID):
    return 'http://localhost:8000/up/' + str(userID) + '/job/' + str(jobID) + '/authorization/'

r = requests.get(url = jobAPIurl(2))

if r.status_code != 200:
    print(str(r.status_code))
    exit()

data = r.json()

if data['count'] > 0:
    print('Jobs are already exist.\n')
    exit()

jobs = [
        { # job number: 0
            "name": "job 1",
            "creator_id": 1,
            "parent_id": None
        },
        { # job number: 1
            "name": "job 2",
            "creator_id": 2,
            "parent_id": None
        },
        { # job number: 2
            "name": "job 3",
            "creator_id": 3,
            "parent_id": None
        },
        { # job number: 3
            "name": "job 4",
            "creator_id": 2,
            "parent_id": None
        },
        { # job number: 4
            "name": "job 5",
            "creator_id": 2,
            "parent_id": None
        },
        { # job number: 5
            "name": "job 6",
            "creator_id": 2,
            "parent_id": None
        },
        { # job number: 6
            "name": "job 7",
            "creator_id": 2,
            "parent_id": None
        },

        
        { # job number: 7
            "name": "job 10",
            "creator_id": 2,
            "parent_id": 1
        },
        { # job number: 8
            "name": "job 11",
            "creator_id": 2,
            "parent_id": 1
        },
        { # job number: 9
            "name": "job 12",
            "creator_id": 2,
            "parent_id": 1
        },
        { # job number: 10
            "name": "job 13",
            "creator_id": 3,
            "parent_id": 2
        },
        
        { # job number: 11
            "name": "job 20",
            "creator_id": 2,
            "parent_id": 7
        },
        { # job number: 12
            "name": "job 21",
            "creator_id": 2,
            "parent_id": 7
        },
        { # job number: 13
            "name": "job 22",
            "creator_id": 2,
            "parent_id": 8
        },

        { # job number: 14
            "name": "job 30",
            "creator_id": 2,
            "parent_id": 11
        },
    ]

for job in jobs:
    if job["parent_id"] is not None:
        if jobs[job["parent_id"]]["id"] is None:
            continue
        job["parent_id"] = jobs[job["parent_id"]]["id"]
    r = requests.post(url = jobAPIurl(job['creator_id']), data = job)
    if r.status_code != 201:
        print([jobAPIurl(job['creator_id']), r.status_code, data])
    else:
        job['id'] = r.json()['id']


print('Jobs initialized properly.')



for userID in range(1,10): # iterate through users
    for job in jobs:
        if job['creator_id'] == userID and 'id' in job: ## "privilege" check

            ## Add member privilege for admin to every job
            if job['creator_id'] != 1:
                data = {"job_privilege_id": 1, "user_id": 1}
                r = requests.post(url = jobAuthorizationAPIurl(job['creator_id'], job['id']), data = data)
                if r.status_code != 201:
                    print([jobAuthorizationAPIurl(job['creator_id'], job['id']), r.status_code, data])

            ## Add memeber privilege to user 5 only where job parent id is NULL
            if job['parent_id'] == None:
                data = {"job_privilege_id": 1, "user_id": 5}
                r = requests.post(url = jobAuthorizationAPIurl(job['creator_id'], job['id']), data = data)
                if r.status_code != 201:
                    print([jobAuthorizationAPIurl(job['creator_id'], job['id']), r.status_code, data])

            if job['parent_id'] == jobs[1]["id"]:
                data = {"job_privilege_id": 1, "user_id": 6}
                r = requests.post(url = jobAuthorizationAPIurl(job['creator_id'], job['id']), data = data)
                if r.status_code != 201:
                    print([jobAuthorizationAPIurl(job['creator_id'], job['id']), r.status_code, data])

            if job['parent_id'] == jobs[11]["id"]:
                data = {"job_privilege_id": 1, "user_id": 7}
                r = requests.post(url = jobAuthorizationAPIurl(job['creator_id'], job['id']), data = data)
                if r.status_code != 201:
                    print([jobAuthorizationAPIurl(job['creator_id'], job['id']), r.status_code, data])


print('Privileges initialized properly.')
print('')
