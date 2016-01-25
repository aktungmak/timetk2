from __future__ import unicode_literals

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

    # TODO running should be a computed property
    # that is true if this netcode has any Events
    # which do not have an end time
    running = models.BooleanField(default=False)
    def __str__(self):
        return "%s-%s: %s" % (self.network,
                              self.activity,
                              self.name)

@python_2_unicode_compatible
class Event(models.Model):
    netcode = models.ForeignKey(Netcode, on_delete=models.CASCADE)
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "%s -> %s" % (self.start, self.end)