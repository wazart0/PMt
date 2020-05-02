import requests



url = 'http://localhost:8000/graphql/'


request_get_users = '''
{
  users {
    id
  }
}
'''

request_create_work_week = '''
mutation {{
  createAvailability (
    user: {user}
	  start: "{start}"
    duration: "{duration}"
    repeatInterval: "{repeat}"
    # until: "{until}"
  ) {{
    availability {{
      id
    }}
  }}
}}
'''

work_week = [
    ['2020-01-01T09:00:00+00:00', '8h', '7d', None],
    ['2020-01-02T09:00:00+00:00', '8h', '7d', None],
    ['2020-01-03T09:00:00+00:00', '8h', '7d', None],
    ['2020-01-06T09:00:00+00:00', '8h', '7d', None],
    ['2020-01-07T09:00:00+00:00', '8h', '7d', None]
]



print('Creating work week.')

r_users = requests.post(url=url, json={"query": request_get_users})

for user in r_users.json()['data']['users']:
    for day in work_week:
        data = request_create_work_week.format(user=user['id'], start=day[0], duration=day[1], repeat=day[2], until=day[3])
        r = requests.post(url=url, json={"query": data})
        if r.status_code != 200:
            print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))


print('Work week created.')