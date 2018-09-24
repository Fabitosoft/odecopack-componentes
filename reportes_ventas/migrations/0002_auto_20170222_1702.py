# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 22:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes_ventas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicoventa',
            name='t_1_venta_neta_acum',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='historicoventa',
            name='t_2_venta_neta_acum',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='historicoventa',
            name='t_3_venta_neta_acum',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='historicoventa',
            name='t_venta_neta_acum',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='historicoventa',
            name='t_1_venta_neta',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='historicoventa',
            name='t_2_venta_neta',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='historicoventa',
            name='t_3_venta_neta',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='historicoventa',
            name='t_venta_neta',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
    ]
