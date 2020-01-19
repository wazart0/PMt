from django.db import connection

print('Inserting job privileges...')

privileges = {
    'observer': 'Reporter',
    'add_user': 'Add new user',
    'remove_user': 'Remove user',
    'description': 'Modify description',
    'give_up_child': 'Change childs parent',
    'manage_privileges': 'Manage users privileges',
    'remove_job': 'Remove job',

    'add_child': 'Add sub-job',
    'manage_childs': 'Edit sub-jobs'}

cursor = connection.cursor()
cursor.execute("select count(*) from jobs_privileges;")
if cursor.fetchone()[0] != len(privileges):
    insert = 'insert into jobs_privileges (code_name, name) values' 
    for i in privileges:
        insert += ' (\'' + i + '\', \'' + privileges[i] + '\'),'
    insert = insert[:-1]
    insert += ';'
    cursor.execute(insert)
else:
    print('Job privileges already inserted.')



print('Inserting job types...')

types = {
    'default': '#FFFFFF',} # TODO define more basic types

cursor = connection.cursor()
cursor.execute("select count(*) from jobs_type;")
if cursor.fetchone()[0] != len(types):
    insert = 'insert into jobs_type (name, color) values' 
    for i in types:
        insert += ' (\'' + i + '\', \'' + types[i] + '\'),'
    insert = insert[:-1]
    insert += ';'
    cursor.execute(insert)
else:
    print('Job types already inserted.')



print('Inserting job statuses...')

statuses = {
    'Created': 'Job created',} # TODO define more basic statuses

cursor = connection.cursor()
cursor.execute("select count(*) from jobs_status;")
if cursor.fetchone()[0] != len(statuses):
    insert = 'insert into jobs_status (name, description) values' 
    for i in statuses:
        insert += ' (\'' + i + '\', \'' + statuses[i] + '\'),'
    insert = insert[:-1]
    insert += ';'
    cursor.execute(insert)
else:
    print('Job statuses already inserted.')
