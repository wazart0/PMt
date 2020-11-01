import requests



url = 'http://localhost:8090/v1/graphql'
# url = 'http://51.83.129.102:8090/v1/graphql/'




query_create_work_week = open('createCalendar.graphql', 'r').read()



name = '5x8h workweek'
description = 'People available 8h per day with office hours from 9AM to 5PM'
calculation_details = \
	'''
		{
			weekdays: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
			start_hour: "T09:00:00+00:00",
			finish_hour: "T17:00:00+00:00"
		}
	'''


print('Creating work week.')


data = query_create_work_week \
	.replace('{name}', name) \
	.replace('{description}', description) \
	.replace('{calculation_details}', str(calculation_details))


r_users = requests.post(url=url, json={"query": data})
if r_users.status_code != 200 or 'errors' in r_users.json():
	print('ERROR: users not found: ' + str(url) + ' ' + str(r_users.status_code) + ' ' + str(r_users.json()))
	print(data)
	exit()


print('Work week created.')