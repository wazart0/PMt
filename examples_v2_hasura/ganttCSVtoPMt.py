import requests
import pandas._libs.hashtable
import os
import uuid
# import numpy as np

path = os.path.dirname(os.path.realpath(__file__)) + '/'
print(path)



url = 'http://localhost:8090/v1/graphql'
# url = 'http://51.83.129.102:8000/graphql/'

input_csv_path = '../examples/tools/'
# input_csv = 'BNext-optimization.csv'
input_csv = 'test_FS_only.csv'

creator_id = 1
import_to_project_id = None
default_baseline_id = None



print('URL: ' + url)
print('Creator id: ' + str(creator_id))

gantt_base_columns = {
	'ID': 'Int64',
	'Name': str,
	'Duration': 'Int64',
	'Predecessors': str,
	'Outline number': str
}




query_create_project_root = open('createProjectRoot.graphql', 'r').read()
query_create_project_child =  open('createProjectChild.graphql', 'r').read()
query_create_project_depenedency =  open('createProjectDependency.graphql', 'r').read()

csv = pandas.read_csv(path + input_csv_path + input_csv, dtype=gantt_base_columns, parse_dates=['Begin date', 'End date'])


if import_to_project_id is None:	
	import_to_project_id = uuid.uuid1()
	default_baseline_id = uuid.uuid1()
	data = query_create_project_root \
		.replace('{project_id}', str(import_to_project_id)) \
		.replace('{baseline_id}', str(default_baseline_id)) \
		.replace('{name}', str(input_csv)) \
		.replace('{label}', str('root'))
	r = requests.post(url=url, json={"query": data})
	if r.status_code != 200 or 'errors' in r.json():
		print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(data))
		exit()

print('Root project ID: ' + str(import_to_project_id))

print('=== PROJECTS INGESTION ===')

pmt_id = {}
translation_id = {}

for index, row in csv.iterrows():
	print([row['ID'], row['Name'].strip(), row['Duration'], row['Predecessors'], row['Outline number']])

	parent_project_id = str(import_to_project_id) if len(row['Outline number'].rsplit('.', 1)) == 1 else str(pmt_id[row['Outline number'].rsplit('.', 1)[0]])
	data = query_create_project_child \
		.replace('{project_id}', str(uuid.uuid1())) \
		.replace('{parent_project_id}', str(parent_project_id)) \
		.replace('{baseline_id}', str(default_baseline_id)) \
		.replace('{name}', str(row['Name'].strip())) \
		.replace('{label}', str(row['Outline number'])) \
		.replace('{worktime}', str(row['Duration']) + 'd') \
		.replace('{start}', str(row['Begin date'])) \
		.replace('{finish}', str(row['End date']))
	r = requests.post(url=url, json={"query": data})

	if r.status_code != 200 or 'errors' in r.json():
		print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(data))
		exit()
	else:
		pmt_id[row['Outline number']] = r.json()['data']['insert_project_one']['id']
		translation_id[row['ID']] = r.json()['data']['insert_project_one']['id']

print('=== PREDECESSORS INGESTION ===')

for index, row in csv.iterrows():
	if pandas.notna(row['Predecessors']):
		print([row['ID'], row['Name'].strip(), row['Duration'], row['Predecessors'], row['Outline number']])
		for dependence in row['Predecessors'].split(';'):
			formatted = dependence.split('-')[1] if len(dependence.split('-')) > 1 else 'FS', int(dependence.split('-')[0])
			data = query_create_project_depenedency \
				.replace('{baseline_id}', str(default_baseline_id)) \
				.replace('{project_id}', str(translation_id[row['ID']])) \
				.replace('{predecessor_id}', str(translation_id[int(dependence.split('-')[0])])) \
				.replace('{type}', str(dependence.split('-')[1] if len(dependence.split('-')) > 1 else 'FS'))
			r = requests.post(url=url, json={"query": data})
			if r.status_code != 200 or 'errors' in r.json():
				print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(data))
				exit()

print('=== INGESTION DONE ===')

# print(csv)




# request_create_baseline = '''
# mutation {{
# 	createBaseline (
# 		project: {project_id}
# 		name: "automated from ganttCSV"
# 		default: true
# 	) {{
# 		baseline {{
# 			id
# 		}}
# 	}}
# }}
# '''

# request_propose_timeline = '''
# mutation {{
# 	updateBaseline (
# 		baseline: {baseline_id} 
# 		proposeTimeline: true
# 	) {{
#     baseline {{
#       	id
#     }}
#   }}
# }}
# '''


# print('=== CREATE BASELINE ===')

# data = request_create_baseline.format(project_id=import_to_project_id)
# r = requests.post(url=url, json={"query": data})
# if r.status_code != 200 or 'errors' in r.json():
# 	print('ERROR: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
# 	exit()
# baseline_id = r.json()['data']['createBaseline']['baseline']['id']

# print('=== PROPOSE BASELINE ===')

# data = request_propose_timeline.format(baseline_id=baseline_id)
# r = requests.post(url=url, json={"query": data})
# if r.status_code != 200 or 'errors' in r.json():
# 	print('ERROR: record not ingested: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
# 	exit()

# print('=== FINISHED ===')
# print('')

# print('Created project ID: ' + str(import_to_project_id))
# print('Created baseline ID: ' + str(baseline_id))
# print('')

