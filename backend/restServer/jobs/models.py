from django.db import models
from ums.models import User

# Create your models here.

class JobStatus(models.Model):
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    # some icons, etc

    objects = models.Manager()

class JobType(models.Model):
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)

    objects = models.Manager()

class JobStatusType(models.Model):
    jobType = models.ForeignKey(null = False, to = JobType, on_delete = models.CASCADE)
    jobStatus = models.ForeignKey(null = False, to = JobStatus, on_delete = models.CASCADE)
    class Meta:
        unique_together = ('jobType', 'jobStatus')
        
    objects = models.Manager()


# class JobPrivileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
#     None

class Job(models.Model):
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT)
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    closed = models.DateTimeField(null = True)
    parent = models.ForeignKey(to = 'self', null = True, on_delete = models.CASCADE)
    status = models.ForeignKey(null = True, to = JobStatus, on_delete = models.PROTECT)
    childType = models.ForeignKey(to = JobType, on_delete = models.PROTECT)
    # plannedStart = models.DateTimeField() # has to be extracted to baselines
    # plannedFinish = models.DateTimeField()

    objects = models.Manager()

