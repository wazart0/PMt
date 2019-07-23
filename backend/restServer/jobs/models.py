from django.db import models
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
    # some icons, etc

    objects = models.Manager()


class Type(models.Model):
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)

    objects = models.Manager()


class TypeStatuses(models.Model):
    type_id = models.ForeignKey(null = False, to = Type, on_delete = models.CASCADE)
    status_id = models.ForeignKey(null = False, to = Status, on_delete = models.CASCADE)
    class Meta:
        unique_together = ('type_id', 'status_id')
        
    objects = models.Manager()


class Job(models.Model):
    creator_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, related_name = 'job_creator_id')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    closed = models.DateTimeField(null = True)
    parent_id = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE, related_name = 'job_parent_id')
    status_id = models.ForeignKey(null = False, to = Status, on_delete = models.PROTECT, related_name = 'job_status_id')
    child_type_id = models.ForeignKey(null = False, to = Type, on_delete = models.PROTECT, related_name = 'job_child_type_id')
    assignee_id = models.ForeignKey(null = True, to = User, on_delete = models.SET_NULL, related_name = 'job_assignee_id')
    default_baseline_id = models.ForeignKey(null = True, to = 'Baseline', on_delete = models.SET_NULL, related_name = 'job_default_baseline_id')

    objects = models.Manager()

    
class Milestone(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, related_name = 'milestone_job_id')
    creator_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, related_name = 'milestone_creator_id')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    timestamp = models.DateTimeField(null = False)
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)
        
    objects = models.Manager()


class Baseline(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, related_name = 'baseline_job_id')
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
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, related_name = 'execution_job_id')
    user_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, related_name = 'execution_user_id')
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    is_start = models.BooleanField(null = False) # if true job is started, else job execution is stopped

    objects = models.Manager()


class ReportedWorkTime(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, related_name = 'reportedworktime_job_id')
    user_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, related_name = 'reportedworktime_user_id')
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    worktime = models.DurationField(null = False)

    objects = models.Manager()


class Privileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
    name = models.CharField(null = False, max_length = 50)
    codename = models.CharField(null = False, max_length = 50, unique = True)
        
    objects = models.Manager()


class JobAuthorization(models.Model):
    job_id = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False, related_name = 'jobauthorization_job_id')
    privilege_id = models.ForeignKey(null = False, to = Privileges, on_delete = models.CASCADE, editable = False, related_name = 'jobauthorization_privilege_id')
    user_group_id = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, editable = False, related_name = 'jobauthorization_user_group_id')
    
    class Meta:
        unique_together = ('job_id', 'privilege_id', 'user_group_id')
        
    objects = models.Manager()
