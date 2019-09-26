from django.db import connection

cursor = connection.cursor()
cursor.execute("select count(*) from ums_user where id = 1 and email = 'admin@admin.admin';")
if cursor.fetchone()[0] != 1:
    cursor.execute("insert into ums_user (id, email, password, is_active, created, updated) values (1, 'admin@admin.admin', 'pass', True, now(), now());")
