# %%
import requests
import dateutil.parser
from datetime import datetime, timedelta
import pytz
from bidict import bidict
import pandas as pd
import numpy as np


import gspread




# def get_issues(jira_info: dict, label: str, assignee_id: str) -> dict:
#     # example jql: project=pp and labels=p2_pipelines and status was "in development" after -10h and assignee was 557058:d34c4f6a-cba8-4519-be9d-cf727aeb6fbc
#     return requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql=project=pp%20and%20labels="{0}"%20and%20assignee%20was%20{1}%20and%20updatedDate%20%3E%20-{2}'''.format(label, assignee_id, '1w'), auth=(jira_info['username'], jira_info['api_token']))


def get_issues(jira_info: dict, jql: str) -> dict:
    # example jql: project=pp and labels=p2_pipelines and status was "in development" after -10h and assignee was 557058:d34c4f6a-cba8-4519-be9d-cf727aeb6fbc

    max_results = 100
    start_at = 0
    response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql={0}&maxResults={1}&startAt={2}'''.format(jql, max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
    issues = response['issues']
    total = response['total']

    while start_at < total:
        # return issues
        start_at = start_at + max_results
        response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql={0}&maxResults={1}&startAt={2}'''.format(jql, max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
        issues = issues + response['issues']

    return issues


def get_issue_changelog(jira_info: dict, issue_key: str) -> tuple:
    return requests.get('https://tangramcare.atlassian.net/rest/api/latest/issue/{0}?expand=changelog'.format(issue_key), auth=(jira_info['username'], jira_info['api_token'])).json()


def get_timespent_from_tempo(issue_key: str, tempo_token: str) -> float:
    r = requests.get(url="https://api.tempo.io/core/3/worklogs/issue/" + issue_key, headers={"Authorization": "Bearer " + tempo_token})
    return sum([i['timeSpentSeconds'] for i in r.json()['results']]), [{'user': log['author']['displayName'], 'id': log['author']['accountId'], 'worktime': log['timeSpentSeconds'], 'key': issue_key} for log in r.json()['results']]


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






def parse_issues(issues: dict, tempo_token: str) -> dict:
    timelog = []
    parsed_issues = []
    for issue in issues:
        total, details = get_timespent_from_tempo(issue['key'], tempo_token)
        if details:
            timelog = timelog + details
        parsed_issues.append({
            "key": issue['key'], 
            "name": issue['fields']['summary'], 
            "worktime_planned": issue['fields']['timeoriginalestimate'], 
            "worktime_actual": issue['fields']['customfield_11737']*3600. if issue['fields']['customfield_11737'] is not None and total < issue['fields']['customfield_11737']*3600 else total,
            "version": ','.join([i['name'] for i in issue['fields']['fixVersions']]),
            "component": ','.join([i['name'] for i in issue['fields']['components']]),
            "type": issue['fields']['issuetype']['name'],
            "status": issue['fields']['status']['name'],
            "statusCategory": issue['fields']['status']['statusCategory']['name'],
            "origin": issue['fields']['customfield_11748']['value'] if issue['fields']['customfield_11748'] is not None else None,
            "project": issue['fields']['project']['key']
        })
    return parsed_issues, timelog



def get_team_performance_statistics(df_issues: pd.DataFrame, df_timelog: pd.DataFrame) -> pd.DataFrame:
    merged = df_timelog.merge(df_issues[(df_issues.statusCategory == 'Done') & (df_issues.worktime_planned > 0.) & (df_issues.worktime_actual > 0.)][['key', 'worktime_planned', 'worktime_actual']], on='key')
    aggregated = merged.groupby(['user', 'key']).agg({'worktime': 'sum', 'worktime_planned': 'first', 'worktime_actual': 'last'})

    total_worktime_per_person = aggregated[aggregated.worktime > (0.75 * aggregated.worktime_actual)].groupby('user').agg({'worktime': 'sum', 'worktime_planned': 'sum', 'worktime_actual': 'sum'})
    total_worktime_per_person['overtime'] = total_worktime_per_person.worktime_actual - total_worktime_per_person.worktime_planned
    total_worktime_per_person['overtime_%'] = total_worktime_per_person.worktime_actual / total_worktime_per_person.worktime_planned * 100.
    total_worktime_per_person['engagement_in_tasks_%'] = total_worktime_per_person.worktime / total_worktime_per_person.worktime_actual * 100.

    # convert to hours
    total_worktime_per_person.worktime = total_worktime_per_person.worktime/3600.
    total_worktime_per_person.worktime_planned = total_worktime_per_person.worktime_planned/3600.
    total_worktime_per_person.worktime_actual = total_worktime_per_person.worktime_actual/3600.
    total_worktime_per_person.overtime = total_worktime_per_person.overtime/3600.

    total_worktime_per_person['user'] = total_worktime_per_person.index
    total_worktime_per_person = total_worktime_per_person[ ['user'] + [ col for col in total_worktime_per_person.columns if col != 'user' ] ].reset_index(drop=True)

    return total_worktime_per_person




def project_summary(df_issues: pd.DataFrame) -> list:
    def sum_column_by_components(filtered_issues: pd.DataFrame, column: str) -> list:
        return [
            filtered_issues[filtered_issues.component == 'BE'][column].sum()/3600.,
            filtered_issues[filtered_issues.component == 'FE'][column].sum()/3600.,
            filtered_issues[filtered_issues.component == 'QA'][column].sum()/3600.,
            filtered_issues[filtered_issues.component == 'Deployment'][column].sum()/3600.,
            filtered_issues[~filtered_issues.component.isin(['BE', 'FE', 'QA', 'Deployment'])][column].sum()/3600.,
            filtered_issues[column].sum()/3600.
        ]
    
    def count_by_components(filtered_issues: pd.DataFrame) -> list:
        return [
            filtered_issues[filtered_issues.component == 'BE'].shape[0],
            filtered_issues[filtered_issues.component == 'FE'].shape[0],
            filtered_issues[filtered_issues.component == 'QA'].shape[0],
            filtered_issues[filtered_issues.component == 'Deployment'].shape[0],
            filtered_issues[~filtered_issues.component.isin(['BE', 'FE', 'QA', 'Deployment'])].shape[0],
            filtered_issues.shape[0]
        ]

    
    # mvp_issues = df_issues[df_issues.version == 'MVP']
    not_bugs = df_issues[df_issues.type != 'Bug']

    overall_project_summary = [
        sum_column_by_components(not_bugs, 'worktime_planned'),
        sum_column_by_components(not_bugs[not_bugs.statusCategory != 'Done'], 'worktime_planned'),
    ]
    overall_project_summary.append([(a-b)/a*100. for a, b in zip(overall_project_summary[0],overall_project_summary[1])])

    overall_team_performance = [
        sum_column_by_components(not_bugs[not_bugs.statusCategory == 'Done'], 'worktime_planned'),
        sum_column_by_components(not_bugs[not_bugs.statusCategory == 'Done'], 'worktime_actual'),
    ]
    overall_team_performance.append([b/a*100. for a, b in zip(overall_team_performance[0], overall_team_performance[1])])
    overall_team_performance.append(sum_column_by_components(df_issues, 'worktime_actual'))

    for i in range(len(overall_project_summary)):
        for j in range(len(overall_project_summary[i])):
            if str(overall_project_summary[i][j]) == 'nan':
                overall_project_summary[i][j] = '-'
    for i in range(len(overall_team_performance)):
        for j in range(len(overall_team_performance[i])):
            if str(overall_team_performance[i][j]) == 'nan':
                overall_team_performance[i][j] = '-'


    bugs = df_issues[df_issues.type == 'Bug']
    overall_bug_summary = [
        count_by_components(bugs[bugs.statusCategory != 'Done']),
        count_by_components(bugs),
        count_by_components(bugs[bugs.statusCategory == 'To Do']),
        count_by_components(bugs[bugs.statusCategory == 'In Progress']),
        count_by_components(bugs[bugs.statusCategory == 'Done']),
        sum_column_by_components(bugs, 'worktime_actual')
    ]

    return overall_project_summary, overall_team_performance, overall_bug_summary



def get_bug_details(df_issues: pd.DataFrame) -> list:
    def aggregate(filtered_issues: pd.DataFrame, column: str) -> list:
        return [
            filtered_issues[filtered_issues.component == 'BE'].shape[0],
            filtered_issues[filtered_issues.component == 'BE'][column].sum()/3600.,
            filtered_issues[filtered_issues.component == 'FE'].shape[0],
            filtered_issues[filtered_issues.component == 'FE'][column].sum()/3600.,
            filtered_issues[filtered_issues.component == 'QA'].shape[0],
            filtered_issues[filtered_issues.component == 'QA'][column].sum()/3600.,
            filtered_issues[filtered_issues.component == 'Deployment'].shape[0],
            filtered_issues[filtered_issues.component == 'Deployment'][column].sum()/3600.,
            filtered_issues[~filtered_issues.component.isin(['BE', 'FE', 'QA', 'Deployment'])].shape[0],
            filtered_issues[~filtered_issues.component.isin(['BE', 'FE', 'QA', 'Deployment'])][column].sum()/3600.,
            filtered_issues.shape[0],
            filtered_issues[column].sum()/3600.,
        ]

    bugs = df_issues[(df_issues.type == 'Bug') & (df_issues.statusCategory == 'Done')]
    bug_details = []
    for origin in bugs.origin.unique():
        if origin is None:
            bug_details.append(['Needs classification'] + aggregate(bugs[bugs.origin.isnull()], 'worktime_actual'))
        else:
            bug_details.append([origin] + aggregate(bugs[bugs.origin == origin], 'worktime_actual'))

    return bug_details



def analyze_and_send_statistics_to_spreadsheet(df_issues, df_timelog, spreadsheet):

    total_worktime_per_person = get_team_performance_statistics(df_issues, df_timelog)
    overall_project_summary, overall_team_performance, overall_bug_summary = project_summary(df_issues)
    bugs_details = get_bug_details(df_issues)
    print('Issues aggregated.')


    gc = gspread.oauth()
    workbook = gc.open_by_key(spreadsheet)

    sheet_summary = workbook.worksheet('Summary')
    sheet_summary.update('C1', str(datetime.now()))
    sheet_summary.update('C5:H7', overall_project_summary)
    sheet_summary.update('C11:H14', overall_team_performance)
    sheet_summary.update('C18:H23', overall_bug_summary)

    sheet_team_performance = workbook.worksheet('Team performance statistics')
    sheet_team_performance.update('A6:G' + str(total_worktime_per_person.shape[0] + 6), total_worktime_per_person.replace([np.inf, -np.inf], '-').values.tolist())

    sheet_bug_details = workbook.worksheet('Finished bugs details')
    sheet_bug_details.update('B5:N' + str(len(bugs_details) + 5), bugs_details)

    print('Sent to spreadsheet.')




if __name__ == "__main__":

    ## config

    tempo_token = "HswBUrr4tVpvq1YXQjXt5X6ZN4uJvV"

    jira_info = {
        'url': 'https://tangramcare.atlassian.net/',
        'username': 'awaz@ownedoutcomes.com',
        'api_token': '6Pu9J7zSN4wBqwqgSREsAE08',
    }

    spreadsheets = [
        {
            "project": "PP",
            "spreadsheet_id": "1eJJiSHYLUl_GqYKONqfdHoloRDbZMhomok6pJT-7mb0"
        },
        {
            "project": "MC",
            "spreadsheet_id": "1-jtj9rQY8mQJu4han3lRCsD2SB1206yVfsHUZz2cfT4"
        },
        {
            "project": "PT",
            "spreadsheet_id": "1-jtj9rQY8mQJu4han3lRCsD2SB1206yVfsHUZz2cfT4"
        },
        {
            "project": "all",
            "spreadsheet_id": "1HBAKCqiVI3DLRVDsBcT3J8CvdiL5C_PmVltSP-KbOgY"
        }
    ]


    # issues = get_issues(jira_info, 'project=pp and originalEstimate is not EMPTY and status=closed')
    # issues = get_issues(jira_info, 'project=pp and fixVersion=mvp and component=be')
    # issues = get_issues(jira_info, 'project=pp and labels=P2_v3 and fixVersion=mvp and component=be and type!=bug')
    issues = get_issues(jira_info, 'project in (pp, mc)')
    print('Issues acquired.')
    
    parsed_issues, timelog = parse_issues(issues, tempo_token)
    print('Issues parsed.')

    df_issues = pd.DataFrame(parsed_issues)
    df_timelog = pd.DataFrame(timelog)


    analyze_and_send_statistics_to_spreadsheet(df_issues[(df_issues.project == spreadsheets[0]['project']) & ((df_issues.version == 'MVP') | (df_issues.type == 'Bug'))], df_timelog, spreadsheets[0]['spreadsheet_id'])
    analyze_and_send_statistics_to_spreadsheet(df_issues[df_issues.project == spreadsheets[1]['project']], df_timelog, spreadsheets[1]['spreadsheet_id'])

    analyze_and_send_statistics_to_spreadsheet(df_issues, df_timelog, spreadsheets[3]['spreadsheet_id'])






# %%
