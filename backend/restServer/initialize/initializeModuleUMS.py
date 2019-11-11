from django.db import connection


print('Inserting group privileges...')

privileges = {  'member': 'Member', # view only privilege
                'add_user': 'Add new user',
                'remove_user': 'Remove user',
                'description': 'Modify description',
                'active': 'Active/Non-active group',
                'give_up_child': 'Change childs parent',
                'manage_privileges': 'Manage user privilege',
                'add_child': 'Add child group',
                'remove_group': 'Remove group'}

cursor = connection.cursor()
cursor.execute("select count(*) from ums_groupprivileges;")
if cursor.fetchone()[0] != len(privileges):
    insert = 'insert into ums_groupprivileges (code_name, name) values' 
    for i in privileges:
        insert += ' (\'' + i + '\', \'' + privileges[i] + '\'),'
    insert = insert[:-1]
    insert += ';'
    cursor.execute(insert)
else:
    print('Group privileges already inserted.')