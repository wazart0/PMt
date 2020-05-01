import requests
import pandas
# import numpy as np


url = 'http://localhost:8000/graphql/'

# input_csv = 'BNext-optimization.csv'
input_csv = 'test_FS_only.csv'

creator_id = 1
import_to_project_id = None



gantt_base_columns = {
	'ID': 'Int64',
	'Name': str,
	'Duration': 'Int64',
	'Predecessors': str,
	'Outline number': str
}


request_create_project = '''
mutation {{
	createProject (
		creatorId: {creator}
		name: "{name}"
		worktimePlanned: "{worktime}"
		projectType: "Task"
		{belonging}
	) {{
		project {{
			id
		}}
	}}
}}
'''

request_update_project = '''
mutation {{
	updateProject (
		projectId: {project}
		{dependence}
	) {{
		project {{
			id
		}}
	}}
}}
'''

print('=== PROJECTS INGESTION ===')

csv = pandas.read_csv(input_csv, dtype=gantt_base_columns, parse_dates=['Begin date', 'End date'])

if import_to_project_id is None:
	request_create_top_level = '''
	mutation {{
		createProject (
			creatorId: {creator}
			name: "{name}"
			projectType: "Project"
		) {{
			project {{
				id
			}}
		}}
	}}
	'''
	data = request_create_top_level.format(creator=creator_id, name=input_csv)
	r = requests.post(url=url, json={"query": data})
	if r.status_code != 200 or 'error' in r.json():
		print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
	else:
		import_to_project_id = r.json()['data']['createProject']['project']['id']


pmt_id = {}
translation_id = {}

for index, row in csv.iterrows():
	print([row['ID'], row['Name'].strip(), row['Duration'], row['Predecessors'], row['Outline number']])

	belongs_to = 'belongsTo: ' + str(import_to_project_id) if len(row['Outline number'].rsplit('.', 1)) == 1 else 'belongsTo: ' + str(pmt_id[row['Outline number'].rsplit('.', 1)[0]])

	data = request_create_project.format(creator=creator_id, name=row['Name'].strip(), worktime=str(row['Duration']) + 'd', belonging=belongs_to)
	r = requests.post(url=url, json={"query": data})
	if r.status_code != 200:
		print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
	else:
		pmt_id[row['Outline number']] = r.json()['data']['createProject']['project']['id']
		translation_id[row['ID']] = r.json()['data']['createProject']['project']['id']

print('=== PREDECESSORS INGESTION ===')

for index, row in csv.iterrows():
	if pandas.notna(row['Predecessors']):
		print([row['ID'], row['Name'].strip(), row['Duration'], row['Predecessors'], row['Outline number']])
		# TODO resolve issue when there is different predecessor type than FS  <<<<<<<<=========================
		timeline_dependence = 'predecessors:[' + ','.join(['{{dependenceType:"{}",projectId:{}}}'.format(i.split('-')[1] if len(i.split('-')) > 1 else 'FS', translation_id[int(i.split('-')[0])]) for i in row['Predecessors'].split(';')]) + ']'
		print(timeline_dependence)
		data = request_update_project.format(project=translation_id[row['ID']], dependence=timeline_dependence)
		# print(data)
		r = requests.post(url=url, json={"query": data})
		if r.status_code != 200:
			print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))

print('=== INGESTION DONE ===')

# print(csv)




request_create_baseline = '''
mutation {{
	createBaseline (
		projectId: {project_id}
		name: "automated from ganttCSV"
		default: true
	) {{
		baseline {{
			id
		}}
	}}
}}
'''

request_propose_timeline = '''
mutation {{
	updateBaseline (
		baselineId: {baseline_id} 
		proposeTimeline: true
	) {{
    baseline {{
      	id
    }}
  }}
}}
'''


print('=== CREATE BASELINE ===')

data = request_create_baseline.format(project_id=import_to_project_id)
r = requests.post(url=url, json={"query": data})
if r.status_code != 200 or 'error' in r.json():
	print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
baseline_id = r.json()['data']['createBaseline']['baseline']['id']

print('=== PROPOSE BASELINE ===')

data = request_propose_timeline.format(baseline_id=baseline_id)
r = requests.post(url=url, json={"query": data})
if r.status_code != 200 or 'error' in r.json():
	print('WARNING: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))

print('=== FINISHED ===')
print('')

print('Created project ID: ' + str(import_to_project_id))
print('Created baseline ID: ' + str(baseline_id))
print('')

