# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-04 20:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_auto_20170104_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colaborador',
            name='subalternos',
            field=models.ManyToManyField(blank=True, related_name='_colaborador_subalternos_+', to='usuarios.Colaborador'),
        ),
    ]
