import requests



url = 'http://localhost:8000/graphql/'



request_create_work_week = '''
mutation {{
  createAvailability (
	start: "{start}"
    end: "{end}"
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
    ['2020-01-01T09:00:00+00:00', '2020-01-01T17:00:00+00:00', '7d', None],
    ['2020-01-02T09:00:00+00:00', '2020-01-02T17:00:00+00:00', '7d', None],
    ['2020-01-03T09:00:00+00:00', '2020-01-03T17:00:00+00:00', '7d', None],
    ['2020-01-06T09:00:00+00:00', '2020-01-06T17:00:00+00:00', '7d', None],
    ['2020-01-07T09:00:00+00:00', '2020-01-07T17:00:00+00:00', '7d', None]
]

print('Creating work week.')


for i in work_week:
    data = request_create_work_week.format(start=i[0], end=i[1], repeat=i[2], until=i[3])
    r = requests.post(url=url, json={"query": data})
    if r.status_code != 200:
        print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))

print('Work week created.')