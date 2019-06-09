from django.db import models
from ums.models import User

# Create your models here.

class JobStatus(models.Model):
    name = models.CharField(max_length = 30)
    description = models.TextField()
    # some icons, etc

class JobStatusGroup(models.Model):
    name = models.CharField(max_length = 30)
    description = models.TextField()

class JobStatusGroupList(models.Model):
    jobStatusGroup = models.ForeignKey(to = JobStatusGroup, on_delete = models.CASCADE)
    jobStatus = models.ForeignKey(to = JobStatus, on_delete = models.CASCADE)


class JobPrivileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
    None

class Job(models.Model):
    parent = models.ForeignKey(to = 'self', null = True, on_delete = models.CASCADE)
    creator = models.ForeignKey(to = User, on_delete = models.CASCADE)
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)
    closed = models.DateTimeField(null = True)
    childStatusGroup = models.ForeignKey(to = JobStatusGroup, on_delete = models.PROTECT)
    status = models.ForeignKey(to = JobStatus, on_delete = models.PROTECT)
    # plannedStart = models.DateTimeField() # has to be extracted to baselines
    # plannedFinish = models.DateTimeField()
