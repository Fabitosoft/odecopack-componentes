# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 21:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0034_cotizacion_actualmente_cotizador'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='actualmente_cotizador',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
