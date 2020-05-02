# %%
import requests
import pandas as pd
# import numpy as np


url = 'http://localhost:8000/graphql/'

output_csv = 'outfile.csv'



request_propose_timeline = '''
{
  baseline (id: 110) {
    id
    name
    description
    default
    projects {
      project {
        id
        name
      }
	  wbs
      start
      finish
    }
  }
}
'''


r = requests.post(url=url, json={"query": request_propose_timeline})
if r.status_code != 200 or 'error' in r.json():
	print('ERROR: ' + str(url) + str(r.status_code) + str(r.json()))

response = r.json()
# print(response)


gantt_base_columns = {
    'ID': 'Int64',
    'Name': str,
    'Predecessors': str,
    'Outline number': str,
    'Begin date': str,
	'End date': str
}

df = pd.DataFrame(columns=gantt_base_columns)

for project in response['data']['baseline']['projects']:
	row = {
		'ID': project['project']['id'], 
		'Name': project['project']['name'], 
		'Predecessors': None, 
		'Outline number': project['wbs'], 
		'Begin date': str(pd.Timestamp(project['start']).to_pydatetime().strftime('%#m/%#d/%y')), 
		'End date': str(pd.Timestamp(project['finish']).to_pydatetime().strftime('%#m/%#d/%y'))
	}
	df = df.append(row, ignore_index=True)

df.sort_values('Outline number', inplace=True)
df.to_csv(output_csv, index=False)

# %%