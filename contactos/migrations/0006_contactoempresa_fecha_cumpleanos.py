# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-11 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contactos', '0005_auto_20170211_0809'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactoempresa',
            name='fecha_cumpleanos',
            field=models.DateField(blank=True, null=True),
        ),
    ]
