import requests
from atlassian import Jira
import gspread
from math import isclose
import dateutil.parser
from datetime import datetime
import pytz





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


def get_timespent_from_tempo(issue_key: str, tempo_token: str) -> float:
    r = requests.get(url="https://api.tempo.io/core/3/worklogs/issue/" + issue_key, headers={"Authorization": "Bearer " + tempo_token})
    return sum([i['timeSpentSeconds'] for i in r.json()['results']])/3600.


def get_lastly_closed_issues(jira: Jira, label: str) -> list:
    jql = 'project=pp and labels={0} and statusCategory=Done and statusCategoryChangedDate > -4d'.format(label)
    return [issue['key'] for issue in jira.jql(jql, limit=1000)['issues']]





if __name__ == "__main__":

    # Sheets API v4 introduced Usage Limits (as of this writing, 500 requests per 100 seconds per project,
    # and 100 requests per 100 seconds per user). When your application hits that limit, 
    # you get an APIError 429 RESOURCE_EXHAUSTED.


    ## config
    tempo_token = "HswBUrr4tVpvq1YXQjXt5X6ZN4uJvV"
    jira_info = {
        'url': 'https://tangramcare.atlassian.net/',
        'username': 'awaz@ownedoutcomes.com',
        'api_token': '6Pu9J7zSN4wBqwqgSREsAE08',
    }
    jira_column = 15
    duration_column = 12
    estimation_column = 8
    spreadsheets = {
        'P2_v3': '1Z_4BLefvChebM4n9IBKrVkGbuGffN7Dk9cPCpTLr3k0',
        'Tests': '1KceWsG9n2oDcUyMbuzhAehi3yMhwWllKHLjelSPNSOE',
        'P2_pipelines': '1PjTmDUoKFltAYcu90V5V6xSvKNn_9KvMUzrOP7DPdAM'
    }


    ## objects
    jira = Jira(
                url=jira_info['url'],
                username=jira_info['username'],
                password=jira_info['api_token'],
                cloud=True)

    gc = gspread.oauth()


    for spreadsheet in spreadsheets:
        print('Updating: ', spreadsheet)
        workbook = gc.open_by_key(spreadsheets[spreadsheet])
        sheet = workbook.worksheet('Tasks')

        jira_keys = sheet.col_values(jira_column)
        duration = sheet.col_values(duration_column)
        estimation = sheet.col_values(estimation_column)

        no_updated_rows = 0

        for issue_key in get_lastly_closed_issues(jira, spreadsheet):
            value = get_timespent_from_tempo(issue_key, tempo_token)
            if issue_key not in ['PP-986', 'PP-984']:
                if estimation[jira_keys.index(issue_key)] != '' and (len(duration) <= jira_keys.index(issue_key) or duration[jira_keys.index(issue_key)] == '' or not isclose(float(duration[jira_keys.index(issue_key)]), value, abs_tol=0.01)):
                    print('Updating:', issue_key, 'old value:', duration[jira_keys.index(issue_key)] if jira_keys.index(issue_key) < len(duration) else '', 'new value:', value)
                    
                    issue_CL = get_issue_changelog(jira_info, issue_key)
                    # start = get_issue_first_transition_date(issue_CL, 'In Development').strftime("%b %d, %Y %H:%M:%S")
                    # finish = get_issue_last_transition_date(issue_CL, 'Code Review').strftime("%b %d, %Y %H:%M:%S")

                    # sheet.update('J{0}:L{0}'.format(jira_keys.index(issue_key) + 1), [[start, finish, value]])
                    sheet.update('L{0}:L{0}'.format(jira_keys.index(issue_key) + 1), [[value]])

                    no_updated_rows = no_updated_rows + 1
        
        sheet_description = workbook.worksheet('Description')
        sheet_description.update('B21:B22', [[datetime.now().strftime("%b %d, %Y %H:%M:%S")], [no_updated_rows]])
        # sheet_description.update('B22', no_updated_rows)

