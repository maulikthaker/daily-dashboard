from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Posts(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=False,auto_now_add=True )
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title


class RecentAddresses(models.Model):
    address = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=False,auto_now_add=True )
    imageFile = models.CharField(max_length=20, null=True)

class PageCounter(models.Model):
    count       = models.BigIntegerField()
    timestamp   = models.DateTimeField(auto_now=True,auto_now_add=False)
    route       = models.CharField(max_length=20)

class Deals(models.Model):
    timestamp = models.DateTimeField(auto_now=False,auto_now_add=True)

class Note(models.Model):
    pub_date = models.DateTimeField()
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __unicode__(self):
        return self.title