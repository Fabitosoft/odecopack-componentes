# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-14 18:26
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('productos_caracteristicas', '0001_initial'),
        ('productos', '0013_articulocatalogo_origen'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='articulocatalogo',
            managers=[
                ('activos', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='articulocatalogo',
            unique_together=set([('referencia', 'fabricante', 'origen')]),
        ),
    ]
