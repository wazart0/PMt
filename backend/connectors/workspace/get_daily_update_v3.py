# %%
import requests
import dateutil.parser
from datetime import datetime, timedelta
import pytz
from bidict import bidict
import copy

import pandas as pd





def get_issues(jira_info: dict, jql: str) -> list:

    max_results = 100
    start_at = 0
    response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql={0}&maxResults={1}&startAt={2}'''.format(jql, max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
    issues = response['issues']
    total = response['total']
    max_results = response['maxResults']

    while start_at < total:
        # return issues
        start_at = start_at + max_results
        response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql={0}&maxResults={1}&startAt={2}'''.format(jql, max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
        max_results = response['maxResults']
        issues = issues + response['issues']

    return issues


def get_issue_changelog(jira_info: dict, issue_key: str) -> list:
    response = requests.get(jira_info['url'] + 'rest/api/2/issue/{0}/changelog'.format(issue_key), auth=(jira_info['username'], jira_info['api_token'])).json()
    changelog = response['values']
    while 'nextPage' in response:
        response = requests.get(response['nextPage'], auth=(jira_info['username'], jira_info['api_token'])).json()
        changelog = changelog + response['values']
    return changelog


def get_tempo_logs(tempo_token: str, issue_key: str) -> list:
    return requests.get(url="https://api.tempo.io/core/3/worklogs/issue/" + issue_key, headers={"Authorization": "Bearer " + tempo_token}).json()['results']


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


def format_output_v3(daily_status: dict, person: str) -> None:
    if person in daily_status:
        print(person)
        for key in daily_status[person]:
            added_people.append(person)
            print("\t{key}: [{type}] ({status}) {name}".format(
                key=key,
                type=daily_status[person][key]['type'],
                status=daily_status[person][key]['status'],
                name=daily_status[person][key]['name']
            ))
            for tempo_log in daily_status[person][key]['tempo_log']:
                print("\t\t-> {time_spent:.2f}h at {logged_at} {description} {author}".format(
                    time_spent=tempo_log['time_spent']/3600.,
                    logged_at=tempo_log['logged_at'],
                    description=tempo_log['description'],
                    author=tempo_log['author']
                ))
        print()



if __name__ == "__main__":

    ## config

    tempo_token = "x4u6Eq7jM99WGSZt4PBXOTePr2cgB6"
    jira_info = {
        'url': 'https://tangramcare.atlassian.net/',
        'username': 'awaz@ownedoutcomes.com',
        'api_token': '6Pu9J7zSN4wBqwqgSREsAE08',
    }


    team = {
        "PL dev team": [
            "Adrian Zawadzki",
            "Aleksandra Boćkowska",
            "Kamil Chmielewski",
            "Maciej Lubecki",
            "Michal Sochacki",
            "Adrian Branski",
            "Wojtek Kozlowski"
        ],
        "QA team": [
            "Kamil Jabłoński",
            "Monika Konopka",
            "Paulina Buchwald",
            "Piotr Olszewski",
            "Swatantra Parmar",
        ],
        "India team": [
            "Manoj",
            "Paras Verma"
        ],
        "Vegas team": [
            "Chandan Singh",
            "Michael Ghisilieri"
        ]
    }


    ## formatter v3 
    str_last_run = "2021-07-22 17:00"
    last_run = parse_date(str_last_run)

    issues = get_issues(jira_info, '(status in ("In Progress", "QA Review") or updatedDate >= "{0}") and project=pp'.format(str_last_run))
    # issues = get_issues(jira_info, 'key=PP-1787')

    daily_status = {}
    parsed_tempo_logs = []

    print("Number of issues to analyze: ", len(issues))
    for issue in issues:
        base = {
            # "key": issue['key'],
            "type": issue['fields']['issuetype']['name'],
            "name": issue['fields']['summary'],
            "status": issue['fields']['status']['name'],
            "tempo_log": []
            }

        # issue_cl = get_issue_changelog(jira_info, issue['key'])
        # parsed_issue_cl = [
        #     {
        #         "status": "Open (To do)",
        #         "start": parse_date(issue['fields']['created']) # take value form issues
        #         }
        #     ]
        # for log in issue_cl:
        #     if parse_date(log['created']) >= last_run:
        #         for item in log['items']:
        #             if item['field'] == 'status':
        #                 parsed_issue_cl.append({
        #                     "status": item['toString'],
        #                     "start": parse_date(log['created'])
        #                 })
        
        tempo_logs = get_tempo_logs(tempo_token, issue['key'])
        for log in tempo_logs:
            if parse_date(log['startDate'] + ' ' + log['startTime']) >= last_run:
                parsed_log = {
                    "author": log['author']['displayName'],
                    "logged_at": log['startDate'] + ' ' + log['startTime'],
                    "time_spent": log['timeSpentSeconds'],
                    "description": log['description']
                    }
                parsed_tempo_logs.append(parsed_log)

                if parsed_log["author"] not in daily_status:
                    daily_status[parsed_log["author"]] = {}
                if issue['key'] not in daily_status[parsed_log["author"]]:
                    daily_status[parsed_log["author"]][issue['key']] = copy.deepcopy(base)
                    
                daily_status[parsed_log["author"]][issue['key']]['tempo_log'].append(parsed_log)

        if base['status'] in ["In Progress", "QA Review"]:
            if not issue['fields']['assignee']:
                print('none assignee: ', issue['key'])
                continue
            if issue['fields']['assignee']['displayName'] not in daily_status:
                daily_status[issue['fields']['assignee']['displayName']] = {}
            if issue['key'] not in daily_status[issue['fields']['assignee']['displayName']]:
                daily_status[issue['fields']['assignee']['displayName']][issue['key']] = copy.deepcopy(base)

    

    added_people = []
    for t in team:
        print("\n\n" + t + ':')
        for person in team[t]:
            format_output_v3(daily_status, person)

    print("Others:")
    for person in daily_status:
        if person not in added_people:
            format_output_v3(daily_status, person)

    








# %%
