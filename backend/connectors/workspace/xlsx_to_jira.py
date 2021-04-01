import sys
import os
from atlassian import Jira
from bidict import bidict

from openpyxl import load_workbook
from openpyxl.styles import Font




filename = sys.argv[1]
label = sys.argv[2]


jira_info = {
    'url': sys.argv[3],
    'username': sys.argv[4],
    'api_token': sys.argv[5],
}



path = os.path.dirname(os.path.realpath(__file__))



def datetime_to_date_converter(date):
    from datetime import datetime
    from dateutil import parser
    return parser.parse(date).strftime("%Y-%m-%d")

def get_schema_from_sheet(sheet): # TODO schema validation
    schema = {}
    schema['offset_row'] = 1 # offset of WBS: TODO search for WBS
    schema['offset_col'] = 0 # offset of WBS: TODO search for WBS
    
    schema['columns'] = { # TODO make it dynamic
        'WBS': 'A',
        'Name': 'B',
        'Description': 'C',
        'Depends on': 'D',
        'Estimate PM': 'G',
        'Jira ID': 'P',
        'Start time': 'J',
        'Finish time': 'K',
        'Duration [h]': 'L'
    }
    schema['data_offset_row'] = 3

    return schema
    

def wbs_regex_check(string, separator = '.'):
    import re
    return True if re.match('\A([0-9]+\\' + separator + '?)+\Z', string) else False

def wbs_regex_task(string):
    import re
    return True if re.match('\A[0-9]+\Z', string) else False

def check_wbs_level(wbs, separator = '.'):
    return len(wbs.split(separator))


def get_wbs_ancestor(wbs, separator = '.'):
    if len(wbs.split(wbs)) == 1:
        return wbs.split(wbs)[0]
    else:
        return '.'.join(wbs.split('.')[0:-1])


def get_wbs_lowest_level_task_number(wbs, separator = '.'):
    return wbs.split(separator)[-1]


def expand_wbs_range(start, finish, separator = '.'):
    if check_wbs_level(start, separator) != check_wbs_level(finish, separator):
        print('ERROR: WBS range level differs: ', start, ' - ', finish)
        return []
    if get_wbs_ancestor(start, separator) != get_wbs_ancestor(finish, separator):
        print('ERROR: WBS range ancestor differs: ', start, ' - ', finish)
        return []
    lowest_level_task = list(range(int(get_wbs_lowest_level_task_number(start, separator)), 1 + int(get_wbs_lowest_level_task_number(finish, separator))))
    wbs_tasks = []
    for i in lowest_level_task:
        if get_wbs_ancestor(start, separator) == '':
            wbs_tasks.append(str(i))
        else:
            wbs_tasks.append(get_wbs_ancestor(start, separator) + '.' + str(i))
    return wbs_tasks
    
def parse_dependencies(dependency_str, wbs_separator = '.'):
    wbs_tasks = []
    for i in str(dependency_str).split(','):
        if wbs_regex_check(i.strip(), wbs_separator):
            wbs_tasks.append(i)
        else:
            range = i.split('-')
            if len(range) != 2:
                print("ERROR: It is not a range: ", range)
                continue
            if wbs_regex_check(range[0].strip(), wbs_separator) == False or wbs_regex_check(range[1].strip(), wbs_separator) == False:
                print("ERROR: It is not a range: ", range)
                continue
            wbs_tasks = wbs_tasks + expand_wbs_range(range[0].strip(), range[1].strip(), wbs_separator)
    return wbs_tasks



def get_jira_key_for_wbs(schema, wbs):
    i = schema['data_offset_row']
    while sheet[schema['columns']['WBS'] + str(i)].value is not None:
        if wbs == str(sheet[schema['columns']['WBS'] + str(i)].value):
            return str(sheet[schema['columns']['Jira ID'] + str(i)].value)
        i = i + 1 
    return None


def create_or_update_issue(jira, schema, index, project, type, label, parent = None):
    if sheet[schema['columns']['Jira ID'] + str(index)].value is None: # create issue
        issue = jira.issue_create({
            'summary': sheet[schema['columns']['Name'] + str(index)].value,
            'description': sheet[schema['columns']['Description'] + str(index)].value,
            'project': {'key': project},
            'issuetype': {'name': type},
            'parent': {'key': parent},
            'customfield_11701': sheet[schema['columns']['Start time'] + str(index)].value,
            'customfield_11702': sheet[schema['columns']['Finish time'] + str(index)].value,
            # 'customfield_10004': str(float(sheet[schema['columns']['Estimate PM'] + str(index)].value)/4),
            # 'Priority': 'priority',
            # 'Status': 'status',
            # 'Creator': 'creator',
            # 'Assignee': 'assignee',
        })
        sheet[schema['columns']['Jira ID'] + str(index)].value = issue['key']
        sheet[schema['columns']['Jira ID'] + str(index)].hyperlink = jira.url + '/browse/' + issue['key']
        sheet[schema['columns']['Jira ID'] + str(index)].font = Font(underline='single', color='0000FF')
        print(issue)
    else:
        task_json = {
            'summary': sheet[schema['columns']['Name'] + str(index)].value,
            'description': sheet[schema['columns']['Description'] + str(index)].value
        }

        if sheet[schema['columns']['Start time'] + str(index)].value is not None:
            task_json['customfield_11701'] = datetime_to_date_converter(sheet[schema['columns']['Start time'] + str(index)].value)
        if sheet[schema['columns']['Finish time'] + str(index)].value is not None:
            task_json['customfield_11702'] = datetime_to_date_converter(sheet[schema['columns']['Finish time'] + str(index)].value)

        if sheet[schema['columns']['Duration [h]'] + str(index)].value is not None:
            task_json['customfield_10004'] = float(sheet[schema['columns']['Duration [h]'] + str(index)].value)/4
        else:
            if sheet[schema['columns']['Estimate PM'] + str(index)].value is not None:
                task_json['customfield_10004'] = float(sheet[schema['columns']['Estimate PM'] + str(index)].value)/4
                
        jira.issue_update(sheet[schema['columns']['Jira ID'] + str(index)].value, task_json)

    if sheet[schema['columns']['Depends on'] + str(index)].value is not None:
        if sheet[schema['columns']['Depends on'] + str(index)].value != '':
            for dependent_task_wbs in parse_dependencies(sheet[schema['columns']['Depends on'] + str(index)].value):
                fields = {
                    "issuelinks": [
                        {
                            "add": {
                                "type": {
                                    "name": "Gantt End to Start",
                                    "inward": "has to be done after",
                                    "outward": "has to be done before"
                                },
                                "inwardIssue": {
                                    "key": get_jira_key_for_wbs(schema, dependent_task_wbs.strip())
                                }
                            }
                        }
                    ]
                }
                jira.edit_issue(issue_id_or_key=sheet[schema['columns']['Jira ID'] + str(index)].value, fields=fields, notify_users=False)
    jira.edit_issue(issue_id_or_key=sheet[schema['columns']['Jira ID'] + str(index)].value, fields={"labels": [{"add": label}]}, notify_users=False)


def create_or_update_issues(jira, sheet, schema, project, label):
    i = schema['data_offset_row']
    while sheet[schema['columns']['WBS'] + str(i)].value is not None:
        wbs = str(sheet[schema['columns']['WBS'] + str(i)].value)
        if not wbs_regex_check(wbs):
            raise Exception('Problem in WBS number structure: ' + str(wbs))

        if wbs_regex_task(wbs):
            create_or_update_issue(jira=jira, schema=schema, index=i, project=project, type='Task', label=label)
        else:
            import re
            parent = get_jira_key_for_wbs(schema=schema, wbs=re.match('\A[0-9]+', wbs)[0])
            if parent is None:
                raise Exception('Task doesn\'t have a parent: ' + wbs)
            create_or_update_issue(jira=jira, schema=schema, index=i, project=project, type='Sub-task', label=label, parent=parent)
        # if i > schema['data_offset_row'] + 5: # for tests purposes
        #     return
        i = i + 1




if __name__ == "__main__":

    jira = Jira(
            url=jira_info['url'],
            username=jira_info['username'],
            password=jira_info['api_token'],
            cloud=True)

    workbook = load_workbook(filename=path+'/'+filename)
    sheet = workbook['Tasks']

    schema = get_schema_from_sheet(sheet)

    create_or_update_issues(jira=jira, sheet=sheet, schema=schema, project='PP', label=label)

    workbook.save(filename=filename)
    workbook.close()

