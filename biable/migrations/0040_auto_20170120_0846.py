# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-20 13:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0039_remove_movimientoventabiable_item_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facturasbiable',
            options={'permissions': (('ver_info_admon_ventas', 'Ver Info Admon Factura'),)},
        ),
    ]
