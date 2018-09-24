# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-27 22:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0043_auto_20170314_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcotizacion',
            name='cantidad_total',
            field=models.DecimalField(decimal_places=3, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='itemcotizacion',
            name='cantidad_venta_perdida',
            field=models.DecimalField(decimal_places=3, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='itemcotizacion',
            name='motivo_venta_perdida',
            field=models.CharField(default='NA', max_length=120),
        ),
    ]
