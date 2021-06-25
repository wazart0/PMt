# %%
import requests
import dateutil.parser
from datetime import datetime, timedelta
import pytz
from bidict import bidict




# def get_issues(jira_info: dict, label: str, assignee_id: str) -> dict:
#     # example jql: project=pp and labels=p2_pipelines and status was "in development" after -10h and assignee was 557058:d34c4f6a-cba8-4519-be9d-cf727aeb6fbc
#     return requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql=project=pp%20and%20labels="{0}"%20and%20assignee%20was%20{1}%20and%20updatedDate%20%3E%20-{2}'''.format(label, assignee_id, '1w'), auth=(jira_info['username'], jira_info['api_token']))


def get_issues(jira_info: dict) -> dict:
    # example jql: project=pp and labels=p2_pipelines and status was "in development" after -10h and assignee was 557058:d34c4f6a-cba8-4519-be9d-cf727aeb6fbc
    
    max_results = 100
    start_at = 0
    response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql=project%3Dpp AND type%3Dbug&maxResults={1}&startAt={2}'''.format('2w', max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
    issues = response['issues']
    total = response['total']

    while start_at < total:
        start_at = start_at + max_results
        response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql=project%3Dpp AND type%3Dbug&maxResults={1}&startAt={2}'''.format('2w', max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
        issues = issues + response['issues']

    return issues


def get_issue_changelog(jira_info: dict, issue_key: str) -> tuple:
    return requests.get('https://tangramcare.atlassian.net/rest/api/latest/issue/{0}?expand=changelog'.format(issue_key), auth=(jira_info['username'], jira_info['api_token'])).json()


def parse_date(date: str) -> datetime:
    return dateutil.parser.parse(date).astimezone(pytz.UTC)
    

def get_change_transition_date(change: dict, toStatus = None): # if toStatus is None return any status transition date
    for i in change['items']:
        if i['field'] == 'status': 
            if toStatus is None:            return parse_date(change['created']) 
            if i['toString'] == toStatus:   return parse_date(change['created']) 
    return None


def get_issue_first_transition_date(issueCL: dict, toStatus: str):
    for change in reversed(issueCL['changelog']['histories']):
        date = get_change_transition_date(change, toStatus)
        if date is not None:    return date
    return None


def get_issue_last_transition_date(issueCL: dict, toStatus: str):
    for change in issueCL['changelog']['histories']:
        date = get_change_transition_date(change, toStatus)
        if date is not None:    return date
    return None


def getAssignee(change):
    for i in change['items']:
        if i['field'] == 'assignee':
            return {'id': i['to'], 'name': i['toString']}
    return None


def getStatus(change):
    for i in change['items']:
        if i['field'] == 'status':
            return {'id': i['to'], 'name': i['toString']}
    return {}


def getStatusPrevious(change):
    for i in change['items']:
        if i['field'] == 'status':
            return {'id': i['from'], 'name': i['fromString']}
    return {}





# def format_output(response, team_member, i, indent = ''):
#     if response.json()['total'] == 0: return i
#     print(indent, "{0}.".format(i), team_member)
#     j = 1
#     for issue in response.json()['issues']:
#         print(indent + "\t", "{0}.".format(j), issue['key'], issue['fields']['summary'], "(status: {0})".format(issue['fields']['status']['name']))
#         j = j + 1
#     return i + 1



def gather_information_from_issue(issue: dict, response_times: list):

    start = None
    finish = None

    print(issue['key'])
    for change in reversed(issue['changelog']['histories']):
        # print(issue['key'])
        if getStatus(change).get('name') == 'Ready for QA (Resolved)':
            print(getStatus(change).get('name'))
            print(change['created'])
            start = parse_date(change['created'])
            finish = None
        if getStatusPrevious(change).get('name') == 'Ready for QA (Resolved)':
            # if getStatus(change).get('name') == 'QA Review':
            print(getStatus(change).get('name'))
            print(change['created'])
            finish = parse_date(change['created'])

        if finish is not None and start is not None:
            print(finish - start)       
            response_times.append((finish - start).total_seconds()) 
            start = None
            finish = None

    print('')

    return response_times







if __name__ == "__main__":

    ## config

    jira_info = {
        'url': 'https://tangramcare.atlassian.net/',
        'username': 'awaz@ownedoutcomes.com',
        'api_token': '6Pu9J7zSN4wBqwqgSREsAE08',
    }


    be_team = bidict({
        "Wojtek": "557058:6c05dd54-0f1f-49e4-afd2-6dfb20607876",
        "Adrian Z": "557058:d34c4f6a-cba8-4519-be9d-cf727aeb6fbc",
        "Maciej L": "557058:f49e0fa2-d2b9-4905-b3de-0e06a3b247b9",
        "Tomek We": "557058:22ea0feb-6738-482e-8e2a-aadd69535af3",
        "Michal S": "557058:c446e8cc-cdfb-4e24-b227-05894d3478ad",
        "Aleksandra B": "5d1a1058dea8360d16bcfe73",
        "Kamil C": "557058:6fd70538-a4a5-487e-a32e-a7a4871c36d8",
        "Manoj": "5f3e6b201ac29c0045e5dd84"
    })

    qa_team = bidict({
        "Bartek K": "5c7e88a9382437634be23d7c",
        "Monika": "5b713fddaf5e080719bd52d7",
        "Paulina B": "5f9c16337cfc240071a90143",
        "Kamil J": "5d91c4275247770c24541709",
        "Piotr O": "5dc4407628be230df5812284",
        "Swatantra": "5f45642e6db35e0039955bb8"
    })


    backend_services = {
        "p2_pipelines": "O2 grouper pipeline development",
        "p2_v3": "Backend Development"
    }


    ## formatter v2
    response_times = []

    for issue in get_issues(jira_info):
        response_times = gather_information_from_issue(get_issue_changelog(jira_info, issue['key']), response_times)



    response_times = gather_information_from_issue(get_issue_changelog(jira_info, 'PP-1412'), response_times)
    response_times = gather_information_from_issue(get_issue_changelog(jira_info, 'PP-1535'), response_times)

    print(response_times)


    sum = 0.
    for i in response_times:
        sum += i

    print()
    print('Total response time:', timedelta(seconds=sum))

    print('Average response time:', timedelta(seconds=sum/len(response_times)))

    print('Maximum response time:', timedelta(seconds=max(response_times)))

    print('Minimum response time:', timedelta(seconds=min(response_times)))







# %%
