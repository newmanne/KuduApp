# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-01-30 22:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agrotrade', '0006_usersubmission'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubmission',
            name='status',
            field=models.CharField(choices=[('Rev', 'Reviewed'), ('Uns', 'Unseen')], default='Uns', max_length=3),
            preserve_default=False,
        ),
    ]
