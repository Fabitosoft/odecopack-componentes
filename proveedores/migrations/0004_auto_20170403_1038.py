# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-03 15:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0003_proveedor_factor_importacion_aereo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proveedor',
            name='factor_importacion_aereo',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=18),
        ),
    ]
