# %%
import requests
import dateutil.parser
from datetime import datetime, timedelta
import pytz
from bidict import bidict






def get_issues(jira_info: dict) -> dict:
    # example jql: project=pp and labels=p2_pipelines and status was "in development" after -10h and assignee was 557058:d34c4f6a-cba8-4519-be9d-cf727aeb6fbc

    max_results = 100
    start_at = 0
    response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql=project=pp%20and%20updatedDate%20%3E%20-{0}&maxResults={1}&startAt={2}'''.format('2w', max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
    issues = response['issues']
    total = response['total']

    while start_at < total:
        start_at = start_at + max_results
        response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql=project=pp%20and%20updatedDate%20%3E%20-{0}&maxResults={1}&startAt={2}'''.format('2w', max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
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
    return None


def getStatusPrevious(change):
    for i in change['items']:
        if i['field'] == 'status':
            return {'id': i['from'], 'name': i['fromString']}
    return None





# def format_output(response, team_member, i, indent = ''):
#     if response.json()['total'] == 0: return i
#     print(indent, "{0}.".format(i), team_member)
#     j = 1
#     for issue in response.json()['issues']:
#         print(indent + "\t", "{0}.".format(j), issue['key'], issue['fields']['summary'], "(status: {0})".format(issue['fields']['status']['name']))
#         j = j + 1
#     return i + 1



def gather_information_from_issue(issue: dict, daily_update: dict):

    def add_update(issue, current_assignee, current_status):
        if issue['fields']['assignee'] is not None and current_assignee is None:
            current_assignee = {
                "id": issue['fields']['assignee']['accountId'],
                "name": issue['fields']['assignee']['displayName']
            }
        if not current_assignee:
            current_assignee = {'id': None, 'name': None}
        
        print(str(current_assignee['name']) + ':', issue['key'], issue['fields']['summary'], "(actual status: {0})".format(issue['fields']['status']['name']), "(status: {0})".format(current_status))

        if current_assignee['id'] not in daily_update:
            daily_update[current_assignee['id']] = []
        daily_update[current_assignee['id']].append({
            'key': issue['key'],
            'summary': issue['fields']['summary'],
            'status': current_status,
            'actual status': issue['fields']['status']['name'],
            'components': [i['name'] for i in issue['fields']['components']], #issue['fields']['components'],
            'labels': issue['fields']['labels'],
            'type': issue['fields']['issuetype']['name']
        })

    is_added = False

    current_assignee = {}
    current_status = {}

    for change in reversed(issue['changelog']['histories']):
        current_status = current_status if getStatus(change) is None else getStatus(change)
        date_change = parse_date(change['created'])
        prev_status = getStatusPrevious(change)
        if prev_status is not None and prev_status['name'] == 'In Progress' and date_change > datetime.now().astimezone(pytz.UTC) - timedelta(hours=71):
            add_update(issue, current_assignee, prev_status.get('name'))
            is_added = True

        new_assignee = {} if getAssignee(change) is None else getAssignee(change)
        if new_assignee.get('id') != current_assignee.get('id') and current_status.get('name') == 'In Progress' and date_change > datetime.now().astimezone(pytz.UTC) - timedelta(hours=71):
            add_update(issue, current_assignee, current_status.get('name'))
            is_added = True

        current_assignee = current_assignee if new_assignee is None else new_assignee

    # print(i['key'], current_assignee, current_status, i['fields']['resolutiondate'])
    if current_status.get('name') == 'In Progress':
        add_update(issue, current_assignee, current_status.get('name'))
        is_added = True

    if is_added:
        print('')

    return daily_update


def format_output_v2(daily_update: dict, team: bidict):
    for member in team:
        if team[member] in daily_update: 
            print(str(member) + ': ')
            for issue in daily_update[team[member]]:
                print(('' if issue['type'] != 'Bug' else '[Bug] ') + issue['key'], issue['summary'], "(actual status: {0})".format(issue['actual status']), "(status: {0})".format(issue['status']))






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
    daily_update = {}

    for issue in get_issues(jira_info):
        daily_update = gather_information_from_issue(get_issue_changelog(jira_info, issue['key']), daily_update)

    print('\nUpdate from BE team: ')
    format_output_v2(daily_update, be_team)

    print('\nUpdate from QA team: ')
    format_output_v2(daily_update, qa_team)

    print('\nUnassigned: ')
    format_output_v2(daily_update, {None: None})


    # daily_update = gather_information_from_issue(get_issue_changelog(jira_info, "PP-1351"), daily_update)
    # daily_update = gather_information_from_issue(get_issue_changelog(jira_info, "PP-977"), daily_update)

    # print(daily_update)


    ## formatter v1
    # format_data_v1(jira_info, team, backend_services)

    # print("P2:")
    # i = 1
    # for service in backend_services:
    #     print("\t", "{0}.".format(i), backend_services[service])
    #     j = 1
    #     for team_member in team:
    #         j = format_output(get_issues(jira_info, service, team[team_member]), team_member, team[team_member], j, "\t\t")
    #     i = i + 1


    # print("\n\n")

    # print("QA")
    # j = 1
    # for team_member in team:
    #     j = format_output(get_issues(jira_info, 'Tests', team[team_member]), team_member, team[team_member], j)








# %%
