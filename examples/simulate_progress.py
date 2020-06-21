import requests
from datetime import datetime


url = 'http://localhost:8000/graphql/'

baseline_id = 110
simulated_current_date = datetime.fromisoformat('2021-01-01T00:00:00-00:00')


request_get_baseline = '''
{{
  baseline(id: {baseline_id}) {{
    name
    projects {{
      project {{
        id
      }}
      start
      finish
    }}
  }}
}}
'''

request_update_project = '''
mutation {{
  updateProject(
    id: {id} 
    start: "{start}" 
    {include} finish: "{finish}"
  ) {{
    project {{
      id
    }}
  }}
}}
'''


print('Gathering projects...')


r_baseline = requests.post(url=url, json={"query": request_get_baseline.format(baseline_id=baseline_id)})
if r_baseline.status_code != 200 or 'errors' in r_baseline.json():
    print('ERROR: baseline not found: ' + str(url) + str(r_baseline.status_code) + str(r_baseline.json()))
    exit()


print('Updating projects...')



for project in r_baseline.json()['data']['baseline']['projects']:
    project_id = project['project']['id']
    start = datetime.fromisoformat(project['start'])
    finish = datetime.fromisoformat(project['finish'])
    include = ''
    if start > simulated_current_date: continue
    if finish > simulated_current_date: include = '#'

    data = request_update_project.format(id=project_id, start=start.isoformat(), finish=finish.isoformat(), include=include)
    r = requests.post(url=url, json={"query": data})
    if r.status_code != 200 or 'errors' in r.json():
        print('ERROR: project not updated: ' + str(url) + str(r.status_code) + str(r.json()) + str(data))
        exit()

print('Finished.')
