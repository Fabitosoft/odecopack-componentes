# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-14 17:03
from __future__ import unicode_literals

import cotizaciones.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0042_remove_imagencotizacion_nombre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagencotizacion',
            name='imagen',
            field=models.ImageField(upload_to=cotizaciones.models.imagen_upload_to),
        ),
    ]
