from django.db import connection

privileges = {  'member': 'Member', # view only privilege
                'add_user': 'Add new user',
                'remove_user': 'Remove user',
                'description': 'Modify description',
                'active': 'Active/Non-active group',
                'give_up_child': 'Change childs parent',
                'manage_privilege': 'Manage user privilege',
                'adopt_child': 'Add child group'}

cursor = connection.cursor()
cursor.execute("select count(*) from ums_groupprivileges;")
if cursor.fetchone()[0] != len(privileges):
    insert = 'insert into ums_groupprivileges (code_name, name) values' 
    for i in privileges:
        insert += ' (\'' + i + '\', \'' + privileges[i] + '\'),'
    insert = insert[:-1]
    insert += ';'
    cursor.execute(insert)
