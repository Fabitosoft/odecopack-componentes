# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-24 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0021_cotizacion_ciudad_despacho'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcotizacion',
            name='descuento',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='precio',
            field=models.DecimalField(decimal_places=2, max_digits=18),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=18),
        ),
    ]