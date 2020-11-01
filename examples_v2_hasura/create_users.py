import requests
import uuid
import datetime



url = 'http://localhost:8090/v1/graphql'
# url = 'http://51.83.129.102:8090/v1/graphql/'



query_create_user = open('createUserWithDefaultCalendar.graphql', 'r').read()

query_get_calendar = '''
	query getCalendar {
		calendar(where: {name: {_eq: "5x8h workweek"}}) {
			id
		}
	}
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



print('Get "5x8h workweek" calendar ID.')

r = requests.post(url=url, json={"query": query_get_calendar})
if r.status_code != 200 or 'errors' in r.json():
	print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(query_get_calendar))
	exit()

calendar_id = r.json()['data']['calendar'][0]['id']


print('Creating users.')


for i in users:
	data = query_create_user \
		.replace('{user_id}', str(uuid.uuid4())) \
		.replace('{calendar_id}', calendar_id) \
		.replace('{email}', i[0]) \
		.replace('{start}', (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat())
	r = requests.post(url=url, json={"query": data})
	if r.status_code != 200 or 'errors' in r.json():
		print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
		exit()

print('Users created.')