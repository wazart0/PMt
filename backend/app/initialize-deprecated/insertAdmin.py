from django.db import connection

print('Inserting global admin...')

cursor = connection.cursor()
cursor.execute("select count(*) from ums_user where email = 'admin@admin.admin';")
if cursor.fetchone()[0] != 1:
    cursor.execute("insert into ums_user (email, password, is_active, created, updated) values ('admin@admin.admin', 'pass', True, now(), now());")
else:
    print('Admin already exists.')