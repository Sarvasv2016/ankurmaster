# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-10 15:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0013_auto_20160510_2053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='interest2',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='interest3',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='interest4',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='interest5',
        ),
    ]
