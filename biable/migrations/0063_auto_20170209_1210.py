# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0062_auto_20170209_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupocliente',
            name='nombre',
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
