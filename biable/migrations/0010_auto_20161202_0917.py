# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-02 14:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0009_auto_20161202_0908'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movimientoventabiable',
            options={'permissions': (('ver_ventaxvendedor', 'Ver Ventas x Vendedor'), ('ver_ventaxcliente', 'Ver Ventas x Cliente'), ('ver_ventaxclientexano', 'Ver Ventas x Cliente x Año'), ('ver_ventaxmes', 'Ver Ventas x Mes'), ('ver_ventaxlineaxano', 'Ver Ventas x Linea x Año'), ('ver_indicadores_ventas', 'Ver Indicadores de Ventas'))},
        ),
    ]