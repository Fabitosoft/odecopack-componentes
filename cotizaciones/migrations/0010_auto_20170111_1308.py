# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-11 18:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0009_cotizacion_observaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='nro_contacto',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
