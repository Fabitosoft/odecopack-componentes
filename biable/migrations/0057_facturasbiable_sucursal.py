# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 21:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0056_auto_20170206_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='facturasbiable',
            name='sucursal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mis_facturas', to='biable.SucursalBiable'),
        ),
    ]
