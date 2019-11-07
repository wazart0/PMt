import requests


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
    print('\nGroups are already exist.\n')
    exit()

groups = [
        {
            "name": "group 1",
            "creator_id": "1",
            # "parent_id": "1"
        },
        {
            "name": "group 2",
            "creator_id": "2",
            # "parent_id": "1"
        },
        {
            "name": "group 3",
            "creator_id": "3",
            # "parent_id": "1"
        },
        {
            "name": "group 4",
            "creator_id": "2",
            # "parent_id": "1"
        },
        {
            "name": "group 5",
            "creator_id": "2",
            # "parent_id": "1"
        },
        {
            "name": "group 6",
            "creator_id": "2",
            # "parent_id": "1"
        },
        {
            "name": "group 7",
            "creator_id": "2",
            # "parent_id": "1"
        },

        
        {
            "name": "group 10",
            "creator_id": "2",
            "parent_id": "2"
        },
        {
            "name": "group 11",
            "creator_id": "2",
            "parent_id": "2"
        },
        {
            "name": "group 12",
            "creator_id": "2",
            "parent_id": "2"
        },
        {
            "name": "group 13",
            "creator_id": "3",
            "parent_id": "3"
        },
        
        {
            "name": "group 20",
            "creator_id": "2",
            "parent_id": "8"
        },
        {
            "name": "group 21",
            "creator_id": "2",
            "parent_id": "8"
        },
        {
            "name": "group 22",
            "creator_id": "2",
            "parent_id": "9"
        },

        {
            "name": "group 30",
            "creator_id": "2",
            "parent_id": "12"
        },
    ]

for group in groups:
    r = requests.post(url = groupAPIurl(group['creator_id']), data = group)
    if r.status_code != 201:
        raise([groupAPIurl(group['creator_id']), r.status_code, data])

print('Groups initialized properly.\n')



for userID in range(1,10): # iterate through users
    r = requests.get(url = groupAPIurl(userID))
    if r.status_code != 200:
        print([groupAPIurl(userID), r.status_code])
        exit()
    groups = r.json()
    for group in groups['results']:
        if group['creator_id'] == userID: ## "privilege" check

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

            if group['parent_id'] == 2:
                data = {"group_privilege_id": 1, "user_id": 6}
                r = requests.post(url = groupAuthorizationAPIurl(group['creator_id'], group['id']), data = data)
                if r.status_code != 201:
                    print([groupAuthorizationAPIurl(group['creator_id'], group['id']), r.status_code, data])

            if group['parent_id'] == 12:
                data = {"group_privilege_id": 1, "user_id": 7}
                r = requests.post(url = groupAuthorizationAPIurl(group['creator_id'], group['id']), data = data)
                if r.status_code != 201:
                    print([groupAuthorizationAPIurl(group['creator_id'], group['id']), r.status_code, data])


print('Privileges initialized properly.\n')
