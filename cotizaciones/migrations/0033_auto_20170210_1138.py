# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-10 16:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0032_cotizacion_sucursal_sub_empresa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='sucursal_sub_empresa',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Empresa o Sucursal'),
        ),
    ]
