# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-28 21:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0019_vendedorbiable_linea_ventas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendedorbiable',
            name='linea',
        ),
        migrations.AlterField(
            model_name='vendedorbiable',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]