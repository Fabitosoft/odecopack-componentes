# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-08 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geografia_colombia', '0006_auto_20170208_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pais',
            name='nombre',
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
