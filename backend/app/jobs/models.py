from django.db import models, connection
from django.utils import timezone
from ums.models import User, Group

# https://www.villanovau.com/resources/project-management/5-phases-project-management-lifecycle/
# https://redbooth.com/hub/5-easy-steps-in-project-development/



class Status(models.Model):
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    trigger = models.CharField(null = True, default = None, max_length = 1,
                            choices = (
                                ('e', "execute"), # sets start execution while setting this status, sets stop execution while leaving
                                ('t', "executeAndLogTime"), # as above + requires logging time while leaving status or change assignee
                                ('c', "close") # sets close status
                            ))
    # TODO some icons, etc

    objects = models.Manager()



class Type(models.Model):
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)

    objects = models.Manager()



class TypeStatuses(models.Model):
    type_id = models.ForeignKey(null = False, to = Type, on_delete = models.CASCADE, db_column = 'type_id')
    status_id = models.ForeignKey(null = False, to = Status, on_delete = models.CASCADE, db_column = 'status_id')
    class Meta:
        unique_together = ('type_id', 'status_id')
        
    objects = models.Manager()



class Job(models.Model):
    creator_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'creator_id', related_name = 'job_creator_id')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    closed = models.DateTimeField(null = True)
    parent_id = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE, db_column = 'parent_id', related_name = 'job_parent_id')
    type_id = models.ForeignKey(null = False, to = Type, on_delete = models.PROTECT, db_column = 'type_id', related_name = 'job_type_id')
    status_id = models.ForeignKey(null = False, to = Status, on_delete = models.PROTECT, db_column = 'status_id', related_name = 'job_status_id')
    assignee_id = models.ForeignKey(null = True, to = User, on_delete = models.SET_NULL, db_column = 'assignee_id', related_name = 'job_assignee_id')

    default_baseline_id = models.ForeignKey(null = True, to = 'Baseline', on_delete = models.SET_NULL, db_column = 'default_baseline_id', related_name = 'job_default_baseline_id')
    default_child_type_id = models.ForeignKey(null = False, to = Type, on_delete = models.PROTECT, db_column = 'default_child_type_id', related_name = 'job_child_type_id')

    objects = models.Manager()    
    
    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):
        print("Job id: " + str(self.pk))  # TODO remove later
        if self.pk == None:
            insert_user_query = '''
                WITH 
                    tmp_job(id) AS (
                        INSERT INTO jobs_job (creator_id, created, updated, name, closed, parent_id, type_id, status_id, assignee_id, default_baseline_id, default_child_type_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  RETURNING id)
                INSERT INTO jobs_jobauthorization (job_id, privilege_id, group_id, created, authorizer_id)
                    SELECT (SELECT id FROM tmp_job), id, (SELECT id FROM ums_group WHERE is_hidden = True AND creator_id = %s AND name = %s), %s, %s
                        FROM jobs_privileges
                RETURNING job_id;
                '''
            def check(field):
                return None if field is None else field.pk
            ts = timezone.now()
            cursor = connection.cursor()
            cursor.execute(insert_user_query, [
                check(self.creator_id), 
                ts, 
                ts, 
                self.name, 
                self.closed, 
                check(self.parent_id), 
                check(self.type_id), 
                check(self.status_id), 
                check(self.assignee_id), 
                check(self.default_baseline_id), 
                check(self.default_child_type_id),
                check(self.creator_id), str(check(self.creator_id)), ts, check(self.creator_id)])
            row = cursor.fetchall()
            self.pk = row[0][0]
            self.refresh_from_db()
        else:
            models.Model.save(self, force_insert, force_update, using, update_fields)
        print("Job id: " + str(self.pk))  # TODO remove later


    
class Milestone(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, db_column = 'job_id', related_name = 'milestone_job_id')
    creator_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'creator_id', related_name = 'milestone_creator_id')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    timestamp = models.DateTimeField(null = False)
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)
        
    objects = models.Manager()



class Baseline(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, db_column = 'job_id', related_name = 'baseline_job_id')
    number = models.SmallIntegerField(null = False, editable = False)

    begin = models.DateTimeField(null = False)
    worktime = models.DurationField(null = False)

    @property
    def end(self):
        return self.begin + self.worktime
        
    class Meta:
        unique_together = ('number', 'job_id')
        
    objects = models.Manager()



class Execution(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, db_column = 'job_id', related_name = 'execution_job_id')
    user_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'user_id', related_name = 'execution_user_id')
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    is_start = models.BooleanField(null = False) # if true job is started, else job execution is stopped

    objects = models.Manager()



class ReportedWorkTime(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, db_column = 'job_id', related_name = 'reportedworktime_job_id')
    user_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'user_id', related_name = 'reportedworktime_user_id')
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    worktime = models.DurationField(null = False)

    objects = models.Manager()



class Privileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
    name = models.CharField(null = False, max_length = 50)
    code_name = models.CharField(null = False, max_length = 50, unique = True)
        
    objects = models.Manager()



class JobAuthorization(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, db_column = 'job_id', related_name = 'jobauthorization_job_id')
    privilege_id = models.ForeignKey(null = False, to = Privileges, on_delete = models.CASCADE, db_column = 'privilege_id', related_name = 'jobauthorization_privilege_id')
    group_id = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group_id', related_name = 'jobauthorization_group_id')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    authorizer_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'authorizer_id', related_name = 'jobauthorization_authorizer_id')
    
    class Meta:
        unique_together = ('job_id', 'privilege_id', 'group_id')
        
    objects = models.Manager()
