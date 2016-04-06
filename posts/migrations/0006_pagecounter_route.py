# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-25 23:35
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_pagecounter'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecounter',
            name='route',
            field=models.CharField(default=datetime.datetime(2016, 3, 25, 23, 35, 4, 147000, tzinfo=utc), max_length=20),
            preserve_default=False,
        ),
    ]
