# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-15 23:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MHacks', '0007_auto_20160815_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='grad_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
