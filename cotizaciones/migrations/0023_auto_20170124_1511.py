# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-24 20:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0022_auto_20170124_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='descuento',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=18),
        ),
    ]