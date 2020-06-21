import requests



url = 'http://localhost:8000/graphql/'



request_create_user = '''
mutation {{
  createUser ( 
  email: "{email}"
    password: "{password}"
    # creator: {creator}
    ) {{
    user {{
      id
      email
    }}
  }}
}}
'''


users = [
    ['awaz@bcaw.biz', 'qwe', None],
    ['kf@ggg.com', 'qwe', None],
    ['adwaz@bcaw.biz', 'qwe', None],
    ['another@ad.com', 'qwe', None],
    ['next@ad.com', 'qwe', None],
    ['sieg@bcaw.biz', 'qwe', None],
    ['deb@bcaw.biz', 'qwe', None],
    ['kil@ad.com', 'qwe', None],
    ['extra@ad.com', 'qwe', None]
]


print('Creating users.')


for i in users:
    data = request_create_user.format(email=i[0], password=i[1], creator=i[2])
    r = requests.post(url=url, json={"query": data})
    if r.status_code != 200 or 'errors' in r.json():
        print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
        exit()

print('Users created.')