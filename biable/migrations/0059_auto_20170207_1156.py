# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-07 16:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0058_auto_20170207_1150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facturasbiable',
            name='anulada',
        ),
        migrations.AddField(
            model_name='facturasbiable',
            name='activa',
            field=models.BooleanField(default=True),
        ),
    ]
