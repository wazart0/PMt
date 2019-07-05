from django.db import models
from ums.models import User, UserGroup

# https://www.villanovau.com/resources/project-management/5-phases-project-management-lifecycle/
# https://redbooth.com/hub/5-easy-steps-in-project-development/


class JobStatus(models.Model):
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


class JobType(models.Model):
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)

    objects = models.Manager()


class JobStatusType(models.Model):
    jobtype = models.ForeignKey(null = False, to = JobType, on_delete = models.CASCADE)
    jobstatus = models.ForeignKey(null = False, to = JobStatus, on_delete = models.CASCADE)
    class Meta:
        unique_together = ('jobtype', 'jobstatus')
        
    objects = models.Manager()


class Job(models.Model):
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, related_name = 'creator')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    closed = models.DateTimeField(null = True)
    parent = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE)
    status = models.ForeignKey(null = False, to = JobStatus, on_delete = models.PROTECT)
    childtype = models.ForeignKey(null = False, to = JobType, on_delete = models.PROTECT)
    assignee = models.ForeignKey(null = True, to = User, on_delete = models.SET_NULL, related_name = 'assignee')
    defaultbaseline = models.ForeignKey(null = True, to = 'Baseline', on_delete = models.SET_NULL, related_name = 'defaultBaseline')

    objects = models.Manager()

    
class Milestone(models.Model):
    job = models.ForeignKey(null = False, to = Job, related_name = 'milestones', on_delete = models.CASCADE)
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT)
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    timestamp = models.DateTimeField(null = False)
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)
        
    objects = models.Manager()


class Baseline(models.Model):
    job = models.ForeignKey(null = False, to = Job, related_name = 'baselines', on_delete = models.CASCADE, editable = False)
    number = models.SmallIntegerField(null = False, editable = False)

    begin = models.DateTimeField(null = False)
    worktime = models.DurationField(null = False)

    @property
    def end(self):
        return self.begin + self.worktime
        
    class Meta:
        unique_together = ('number', 'job')
        
    objects = models.Manager()


class JobExecution(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False)
    user = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT)
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    isstart = models.BooleanField(null = False) # if true job is started, else job execution is stopped

    objects = models.Manager()


class JobReportedWorkTime(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False)
    user = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT)
    timestamp = models.DateTimeField(null = False, auto_now_add = True)
    worktime = models.DurationField(null = False)

    objects = models.Manager()


class JobPrivileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
    name = models.CharField(null = False, max_length = 50)
    codename = models.CharField(null = False, max_length = 50)
        
    objects = models.Manager()


class JobAuth(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False)
    jobprivileges = models.ForeignKey(null = False, to = JobPrivileges, on_delete = models.CASCADE, editable = False)
    usergroup = models.ForeignKey(null = False, to = UserGroup, on_delete = models.CASCADE, editable = False)
    
    class Meta:
        unique_together = ('job', 'jobprivileges', 'usergroup')
        
    objects = models.Manager()
