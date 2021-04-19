def create_or_update_issues(jira, sheets, schema, project, label, schema_type):
    for sheet in sheets:
        print("current sheet: ", sheet)
        i = schema['data_offset_row']
        none_count = 0
        while none_count < 50:
            if sheet[schema['columns']['WBS'] + str(i)].value is not None:
                wbs = str(sheet[schema['columns']['WBS'] + str(i)].value)
                if not wbs_regex_check(wbs):
                    print('Problem in WBS number structure: ', wbs, ' in sheet: ', sheet)
                    i = i + 1
                    continue

                if sheet[schema['columns']['Name'] + str(i)].value is None or sheet[schema['columns']['Name'] + str(i)].value == '':
                    print('Task do not have any name, wbs: ', wbs, ' in sheet: ', sheet)
                    i = i + 1
                    continue

                create_or_update_issue(jira=jira, sheets=sheets, sheet=sheet, schema=schema, index=i, project=project, type='Task', label=label, schema_type=schema_type)

                none_count = 0
            else:
                none_count = none_count + 1
            i = i + 1