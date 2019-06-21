from django.db import models
from ums.models import User, UserGroup

# Create your models here.

class JobStatus(models.Model):
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    isclosing = models.BooleanField(null = False, default = False)
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

class JobManager(models.Manager):
    def all(self):
        return super().get_queryset()
    def get_queryset(self, user):
        return super().get_queryset().filter(creator=user)

class Job(models.Model):
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, related_name = 'creator')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    closed = models.DateTimeField(null = True)
    parent = models.ForeignKey(to = 'self', null = True, on_delete = models.CASCADE)
    status = models.ForeignKey(null = True, to = JobStatus, on_delete = models.PROTECT)
    childtype = models.ForeignKey(to = JobType, on_delete = models.PROTECT)
    assignee = models.ForeignKey(null = True, to = User, on_delete = models.SET_NULL, related_name = 'assignee')
    defaultbaseline = models.ForeignKey(null = True, to = 'Baseline', on_delete = models.SET_NULL, related_name = 'defaultBaseline')

    objects = models.Manager()
    test = JobManager()

    
class Milestone(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE)
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT)
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)
        
    objects = models.Manager()


class Baseline(models.Model):
    job = models.ForeignKey(null = False, to = Job, on_delete = models.CASCADE, editable = False)
    number = models.SmallIntegerField(null = False, editable = False)

    begin = models.DateTimeField(null = False)
    interval = models.DurationField(null = False)

    class Meta:
        unique_together = ('number', 'job')
        
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
