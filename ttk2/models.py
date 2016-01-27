from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class User(models.Model):
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=50)
    # timezone = models.CharField(max_length=10)

    def __str__(self):
        return self.username

@python_2_unicode_compatible
class Netcode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    network = models.CharField(max_length=100)
    activity = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    enabled = models.BooleanField(default=False)
    # this field will be copied to a new event
    # when the task is complted
    curstart = models.DateTimeField(blank=True, null=True)

    def starttime(self):
        if self.curstart is None:
            return None
        else:
            if self.curstart.date() != datetime.today().date():
                return self.curstart.strftime('%H:%M')+" *"
            else:
                return self.curstart.strftime('%H:%M')

    def __str__(self):
        return "%s-%s: %s" % (self.network,
                              self.activity,
                              self.name)

@python_2_unicode_compatible
class Event(models.Model):
    netcode = models.ForeignKey(Netcode, on_delete=models.CASCADE)
    start = models.DateTimeField(default=None, null=True)
    end = models.DateTimeField(default=None, null=True)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return "%s -> %s" % (self.start, self.end)