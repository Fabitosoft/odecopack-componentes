# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-28 17:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0046_auto_20170328_1158'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemcotizacion',
            old_name='cantidad_total',
            new_name='cantidad_inicial',
        ),
    ]
