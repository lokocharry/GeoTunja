# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rutas', '0007_auto_20160209_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoruta',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterModelTable(
            name='estaciondeservicio',
            table='estacion_de_servicio',
        ),
    ]
