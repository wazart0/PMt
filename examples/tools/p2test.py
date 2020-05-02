import requests


url = 'http://localhost:8000/graphql/'


request_schema = '''
{operationName:null,variables:{},query:{  allDatasets {    id    name    fromTime    toTime    localFileName    uploadStatistics {      uploadStatus      __typename    }    __typename  }}}
'''


r = requests.post(url=url, data=request_schema)

print(r.status_code)
print(r.json())
