# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-13 23:49
from __future__ import unicode_literals

import agrotrade.models
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agrotrade', '0009_auto_20200203_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='TraderBids',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('medium', models.CharField(choices=[('Web', 'Web'), ('CC', 'Call Center'), ('SMS', 'SMS')], editable=False, max_length=5)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('active', models.BooleanField(default=True)),
                ('new', models.BooleanField(default=True)),
                ('valid', models.BooleanField(default=True)),
                ('initial_price', models.PositiveIntegerField(editable=False, null=True)),
                ('initial_quantity', models.PositiveIntegerField(editable=False, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('address', django.contrib.postgres.fields.jsonb.JSONField()),
                ('contact_number', models.CharField(max_length=16)),
                ('expiry_date', models.DateTimeField(default=agrotrade.models.bid_expiry_default)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.UserProfile')),
                ('produce', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.ProduceDefinition')),
                ('tags', models.ManyToManyField(blank=True, to='agrotrade.BidTag')),
            ],
            options={
                'verbose_name_plural': 'Bids',
            },
        ),
    ]