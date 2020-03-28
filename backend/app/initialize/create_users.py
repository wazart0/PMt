import requests



url = 'http://localhost:8000/graphql/'



request_create_user = '''
mutation {{
  createUser ( 
	email: "{email}"
    password: "{password}"
    # creatorId: {creator}
   ) {{
    user {{
      id
      email
    }}
  }}
}}
'''


users = [
    ['awaz@bcaw.biz', 'qwe', None]
]


print('Creating users.')


for i in users:
    data = request_create_user.format(email=i[0], password=i[1], creator=i[2])
    r = requests.post(url=url, json={"query": data})
    if r.status_code != 200:
        print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))

print('Users created.')