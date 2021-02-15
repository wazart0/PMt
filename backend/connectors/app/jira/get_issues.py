from atlassian import Jira
from bidict import bidict


url = 'https://tangramcare.atlassian.net/'
username = 'awaz@ownedoutcomes.com'
api_token = '6Pu9J7zSN4wBqwqgSREsAE08'


# O2 jira fields config
o2_pp_fields = bidict({
    'summary': 'summary',
    'epic': 'customfield_10008',
    'description': 'description',
    'project': 'project',
    'issuetype': 'issuetype',
    'priority': 'priority',
    'labels': 'labels',
    'status': 'status',
    'creator': 'creator',
    'assignee': 'assignee',
    'parent': 'parent',   
})


# docs link: https://atlassian-python-api.readthedocs.io/index.html

class GetIssues(Jira):
    
    def __init__(self, url, username, api_token):
        super().__init__(
            url=url,
            username=username,
            password=api_token,
            cloud=True)

    def get_history(self): # TODO
        print(' TODO ')
