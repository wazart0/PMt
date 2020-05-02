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
    type = models.ForeignKey(null = False, to = Type, on_delete = models.CASCADE, db_column = 'type')
    status = models.ForeignKey(null = False, to = Status, on_delete = models.CASCADE, db_column = 'status')
    class Meta:
        unique_together = ('type', 'status')
        
    objects = models.Manager()



class Job(models.Model):
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'creator', related_name = 'job_creator')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    closed = models.DateTimeField(null = True)
    parent = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE, db_column = 'parent', related_name = 'job_parent')
    type = models.ForeignKey(null = False, to = Type, on_delete = models.PROTECT, db_column = 'type', related_name = 'job_type')
    status = models.ForeignKey(null = False, to = Status, on_delete = models.PROTECT, db_column = 'status', related_name = 'job_status')
    assignee = models.ForeignKey(null = True, to = User, on_delete = models.SET_NULL, db_column = 'assignee', related_name = 'job_assignee')

    default_baseline = models.ForeignKey(null = True, to = 'Baseline', on_delete = models.SET_NULL, db_column = 'default_baseline', related_name = 'job_default_baseline')
    default_child_type = models.ForeignKey(null = False, to = Type, on_delete = models.PROTECT, db_column = 'default_child_type', related_name = 'job_child_type')

    objects = models.Manager()    
    
    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):
        print("Job id: " + str(self.pk))  # TODO remove later
        if self.pk == None:
            insert_user_query = '''
                WITH 
                    tmp_job(id) AS (
                        INSERT INTO jobs_job (creator, created, updated, name, closed, parent, type, status, assignee, default_baseline, default_child_type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  RETURNING id)
                INSERT INTO jobs_jobauthorization (job, privilege, group, created, authorizer)
                    SELECT (SELECT id FROM tmp_job), id, (SELECT id FROM ums_group WHERE is_hidden = True AND creator = %s AND name = %s), %s, %s
                        FROM jobs_privileges
                RETURNING job;
                '''
            def check(field):
                return None if field is None else field.pk
            ts = timezone.now()
            cursor = connection.cursor()
            cursor.execute(insert_user_query, [
                check(self.creator), 
                ts, 
                ts, 
                self.name, 
                self.closed, 
                check(self.parent), 
                check(self.type), 
                check(self.status), 
                check(self.assignee), 
                check(self.default_baseline), 
                check(self.default_child_type),
                check(self.creator), str(check(self.creator)), ts, check(self.creator)])
            row = cursor.fetchall()
            self.pk = row[0][0]
            self.refresh_from_db()
        else:
            models.Model.save(self, force_insert, force_update, using, update_fields)
        print("Job id: " + str(self.pk))  # TODO remove later


    
class Milestone(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, db_column = 'job', related_name = 'milestone_job')
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'creator', related_name = 'milestone_creator')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    timestamp = models.DateTimeField(null = False)
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)
        
    objects = models.Manager()



class Baseline(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, db_column = 'job', related_name = 'baseline_job')
    number = models.SmallIntegerField(null = False, editable = False)

    start = models.DateTimeField(null = False)
    worktime = models.DurationField(null = False)

    @property
    def finish(self):
        return self.start + self.worktime
        
    class Meta:
        unique_together = ('number', 'job')
        
    objects = models.Manager()



class Execution(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, db_column = 'job', related_name = 'execution_job')
    user = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'user', related_name = 'execution_user')
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    is_start = models.BooleanField(null = False) # if true job is started, else job execution is stopped

    objects = models.Manager()



class ReportedWorkTime(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, db_column = 'job', related_name = 'reportedworktime_job')
    user = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'user', related_name = 'reportedworktime_user')
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    worktime = models.DurationField(null = False)

    objects = models.Manager()



class Privileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
    name = models.CharField(null = False, max_length = 50)
    code_name = models.CharField(null = False, max_length = 50, unique = True)
        
    objects = models.Manager()



class JobAuthorization(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, db_column = 'job', related_name = 'jobauthorization_job')
    privilege = models.ForeignKey(null = False, to = Privileges, on_delete = models.CASCADE, db_column = 'privilege', related_name = 'jobauthorization_privilege')
    group = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group', related_name = 'jobauthorization_group')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    authorizer = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'authorizer', related_name = 'jobauthorization_authorizer')
    
    class Meta:
        unique_together = ('job', 'privilege', 'group')
        
    objects = models.Manager()
