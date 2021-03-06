# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-05 13:57
from __future__ import unicode_literals

import agrotrade.models
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BidTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=80)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='FarmerAsks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('medium', models.CharField(choices=[('Web', 'Web'), ('CC', 'Call Center')], editable=False, max_length=5)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('active', models.BooleanField(default=True)),
                ('new', models.BooleanField(default=True)),
                ('valid', models.BooleanField(default=True)),
                ('initial_price', models.PositiveIntegerField(editable=False, null=True)),
                ('initial_quantity', models.PositiveIntegerField(editable=False, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('address', django.contrib.postgres.fields.jsonb.JSONField()),
                ('available_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateTimeField(default=agrotrade.models.ask_expiry_default)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('delivery', models.CharField(choices=[('Y', 'Yes'), ('N', 'No')], default='N', max_length=1)),
            ],
            options={
                'verbose_name_plural': 'Asks',
            },
        ),
        migrations.CreateModel(
            name='FavoriteAsk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_favorite', models.BooleanField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('ask', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.FarmerAsks')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProduceDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('produce_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Produce name')),
                ('display_name', models.CharField(blank=True, max_length=100)),
                ('display_name_en_us', models.CharField(blank=True, max_length=100, null=True)),
                ('display_name_lug', models.CharField(blank=True, max_length=100, null=True)),
                ('display_name_luo', models.CharField(blank=True, max_length=100, null=True)),
                ('display_name_run', models.CharField(blank=True, max_length=100, null=True)),
                ('display_name_es', models.CharField(blank=True, max_length=100, null=True)),
                ('active', models.BooleanField()),
                ('conversion_factor', models.FloatField(default=1, verbose_name='Conversion from units to kgs')),
            ],
            options={
                'verbose_name_plural': 'Produce Description',
            },
        ),
        migrations.CreateModel(
            name='SavedSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_price', models.IntegerField(blank=True, null=True)),
                ('max_price', models.IntegerField(blank=True, null=True)),
                ('min_quantity', models.IntegerField(blank=True, null=True)),
                ('max_quantity', models.IntegerField(blank=True, null=True)),
                ('sw_latlng', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('ne_latlng', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('max_age', models.IntegerField(blank=True, null=True)),
                ('time', models.FloatField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_seen_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('active', models.BooleanField(default=True)),
                ('state', models.CharField(choices=[('1', 'Notified'), ('2', 'To notify')], default='1', max_length=1)),
            ],
            options={
                'verbose_name_plural': 'Saved Searches',
            },
        ),
        migrations.CreateModel(
            name='UnitsDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='unit')),
                ('code_en_us', models.CharField(max_length=10, null=True, unique=True, verbose_name='unit')),
                ('code_lug', models.CharField(max_length=10, null=True, unique=True, verbose_name='unit')),
                ('code_luo', models.CharField(max_length=10, null=True, unique=True, verbose_name='unit')),
                ('code_run', models.CharField(max_length=10, null=True, unique=True, verbose_name='unit')),
                ('code_es', models.CharField(max_length=10, null=True, unique=True, verbose_name='unit')),
                ('unit_name', models.CharField(max_length=50, unique=True)),
                ('unit_name_en_us', models.CharField(max_length=50, null=True, unique=True)),
                ('unit_name_lug', models.CharField(max_length=50, null=True, unique=True)),
                ('unit_name_luo', models.CharField(max_length=50, null=True, unique=True)),
                ('unit_name_run', models.CharField(max_length=50, null=True, unique=True)),
                ('unit_name_es', models.CharField(max_length=50, null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Units Description',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firebase', models.CharField(error_messages={'unique': 'A user with that firebase credential already exists.'}, max_length=150, null=True, unique=True)),
                ('phone_number', models.CharField(max_length=16, null=True, unique=True)),
                ('primary_location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('comments', models.TextField(blank=True, max_length=400)),
                ('language', models.CharField(choices=[('en-us', 'English'), ('lug', 'Luganda'), ('luo', 'Luo'), ('run', 'Runyakitara'), ('es', 'Spanish')], default='en-us', max_length=10)),
                ('notification_key', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=300)),
                ('is_used', models.BooleanField(default=False)),
                ('verified_on', models.DateTimeField(blank=True, null=True)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='savedsearch',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.UserProfile'),
        ),
        migrations.AddField(
            model_name='savedsearch',
            name='produce',
            field=models.ManyToManyField(to='agrotrade.ProduceDefinition'),
        ),
        migrations.AddField(
            model_name='producedefinition',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.UnitsDefinition'),
        ),
        migrations.AddField(
            model_name='favoriteask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.UserProfile'),
        ),
        migrations.AddField(
            model_name='farmerasks',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.UserProfile'),
        ),
        migrations.AddField(
            model_name='farmerasks',
            name='payment_methods',
            field=models.ManyToManyField(to='agrotrade.PaymentMethod'),
        ),
        migrations.AddField(
            model_name='farmerasks',
            name='produce',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agrotrade.ProduceDefinition'),
        ),
        migrations.AddField(
            model_name='farmerasks',
            name='tags',
            field=models.ManyToManyField(blank=True, to='agrotrade.BidTag'),
        ),
        migrations.AlterUniqueTogether(
            name='favoriteask',
            unique_together=set([('user', 'ask')]),
        ),
    ]
