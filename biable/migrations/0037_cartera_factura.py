# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-19 20:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0036_movimientoventabiable_factura'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartera',
            name='factura',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mis_cartera_venta', to='biable.FacturasBiable'),
        ),
    ]
