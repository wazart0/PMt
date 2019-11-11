import requests

print('Creating example groups...')

def groupAPIurl(userID):
    return 'http://localhost:8000/up/' + str(userID) + '/group/'
    
def groupAuthorizationAPIurl(userID, groupID):
    return 'http://localhost:8000/up/' + str(userID) + '/group/' + str(groupID) + '/authorization/'

r = requests.get(url = groupAPIurl(1))

if r.status_code != 200:
    print(str(r.status_code))
    exit()

data = r.json()

if data['count'] > 1:
    print('Groups are already exist.\n')
    exit()

groups = [
        { # group number: 0
            "name": "group 1",
            "creator_id": 1,
            "parent_id": None
        },
        { # group number: 1
            "name": "group 2",
            "creator_id": 2,
            "parent_id": None
        },
        { # group number: 2
            "name": "group 3",
            "creator_id": 3,
            "parent_id": None
        },
        { # group number: 3
            "name": "group 4",
            "creator_id": 2,
            "parent_id": None
        },
        { # group number: 4
            "name": "group 5",
            "creator_id": 2,
            "parent_id": None
        },
        { # group number: 5
            "name": "group 6",
            "creator_id": 2,
            "parent_id": None
        },
        { # group number: 6
            "name": "group 7",
            "creator_id": 2,
            "parent_id": None
        },

        
        { # group number: 7
            "name": "group 10",
            "creator_id": 2,
            "parent_id": 1
        },
        { # group number: 8
            "name": "group 11",
            "creator_id": 2,
            "parent_id": 1
        },
        { # group number: 9
            "name": "group 12",
            "creator_id": 2,
            "parent_id": 1
        },
        { # group number: 10
            "name": "group 13",
            "creator_id": 3,
            "parent_id": 2
        },
        
        { # group number: 11
            "name": "group 20",
            "creator_id": 2,
            "parent_id": 7
        },
        { # group number: 12
            "name": "group 21",
            "creator_id": 2,
            "parent_id": 7
        },
        { # group number: 13
            "name": "group 22",
            "creator_id": 2,
            "parent_id": 8
        },

        { # group number: 14
            "name": "group 30",
            "creator_id": 2,
            "parent_id": 11
        },
    ]

for group in groups:
    if group["parent_id"] is not None:
        if groups[group["parent_id"]]["id"] is None:
            continue
        group["parent_id"] = groups[group["parent_id"]]["id"]
    r = requests.post(url = groupAPIurl(group['creator_id']), data = group)
    if r.status_code != 201:
        print([groupAPIurl(group['creator_id']), r.status_code, data])
    else:
        group['id'] = r.json()['id']


print('Groups initialized properly.')



for userID in range(1,10): # iterate through users
    for group in groups:
        if group['creator_id'] == userID and 'id' in group: ## "privilege" check

            ## Add member privilege for admin to every group
            if group['creator_id'] != 1:
                data = {"group_privilege_id": 1, "user_id": 1}
                r = requests.post(url = groupAuthorizationAPIurl(group['creator_id'], group['id']), data = data)
                if r.status_code != 201:
                    print([groupAuthorizationAPIurl(group['creator_id'], group['id']), r.status_code, data])

            ## Add memeber privilege to user 5 only where group parent id is NULL
            if group['parent_id'] == None:
                data = {"group_privilege_id": 1, "user_id": 5}
                r = requests.post(url = groupAuthorizationAPIurl(group['creator_id'], group['id']), data = data)
                if r.status_code != 201:
                    print([groupAuthorizationAPIurl(group['creator_id'], group['id']), r.status_code, data])

            if group['parent_id'] == groups[1]["id"]:
                data = {"group_privilege_id": 1, "user_id": 6}
                r = requests.post(url = groupAuthorizationAPIurl(group['creator_id'], group['id']), data = data)
                if r.status_code != 201:
                    print([groupAuthorizationAPIurl(group['creator_id'], group['id']), r.status_code, data])

            if group['parent_id'] == groups[11]["id"]:
                data = {"group_privilege_id": 1, "user_id": 7}
                r = requests.post(url = groupAuthorizationAPIurl(group['creator_id'], group['id']), data = data)
                if r.status_code != 201:
                    print([groupAuthorizationAPIurl(group['creator_id'], group['id']), r.status_code, data])


print('Privileges initialized properly.')
print('')
