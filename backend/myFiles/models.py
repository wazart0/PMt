from django.db import models



class User(models.Model):
    firstName = models.CharField(max_length = 30)
    lastName = models.CharField(max_length = 30)
    email = models.EmailField(max_length = 50, unique = True, null = False)
    password = models.CharField(max_length = 100)
    createdDateTime = models.DateTimeField(auto_now_add = True)
    updateDateTime = models.DateTimeField(auto_now = True)
    status = models.CharField(null = False, max_length = 1,
                                choices = (
                                    ('a', "Active"),
                                    ('b', "Blocked")
                                ))




class Cost(models.Model):
    beginDateTime = models.DateTimeField(null = False) # date from cost value is valid
    value = models.FloatField(null = False)
    type = models.CharField(null = False, max_length = 1,
                                choices = (
                                    ('f', "Fixed"),
                                    ('s', "Second"),
                                    ('d', "Day"),
                                    ('w', "Week"),
                                    ('m', "Month"),
                                    ('y', "Year")
                                ))

class Resource(models.Model):
    name = models.CharField(max_length = 30)

class ResourceCosts(models.Model):
    cost = models.ForeignKey(to = Cost, on_delete = models.CASCADE)
    resource = models.ForeignKey(to = Resource, on_delete = models.CASCADE)





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
    parent = models.ForeignKey(to = 'self', on_delete = models.CASCADE)
    creator = models.ForeignKey(to = User, on_delete = models.CASCADE)
    createdDateTime = models.DateTimeField(auto_now_add = True)
    updateDateTime = models.DateTimeField(auto_now = True)
    closeDateTime = models.DateTimeField()
    childStatusGroup = models.ForeignKey(to = JobStatusGroup, on_delete = models.PROTECT)
    status = models.ForeignKey(to = JobStatus, on_delete = models.PROTECT)
    # plannedStart = models.DateTimeField() # has to be extracted to baselines
    # plannedFinish = models.DateTimeField()

class JobResources(models.Model):
    job = models.ForeignKey(to = Job, on_delete = models.CASCADE)
    resource = models.ForeignKey(to = Resource, on_delete = models.CASCADE)

    # models.ManyToManyField