# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-25 20:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trabajo_diario', '0010_auto_20170125_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='tareacartera',
            name='descripcion',
            field=models.TextField(blank=True, max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='tareacotizacion',
            name='descripcion',
            field=models.TextField(blank=True, max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='tareaenviotcc',
            name='descripcion',
            field=models.TextField(blank=True, max_length=400, null=True),
        ),
    ]
