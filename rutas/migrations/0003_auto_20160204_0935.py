# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rutas', '0002_auto_20160204_0931'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventoruta',
            name='activo',
        ),
        migrations.RemoveField(
            model_name='eventoruta',
            name='comentario',
        ),
        migrations.RemoveField(
            model_name='eventoruta',
            name='the_geom',
        ),
        migrations.RemoveField(
            model_name='eventoruta',
            name='tipo',
        ),
        migrations.RemoveField(
            model_name='eventoruta',
            name='verificado',
        ),
    ]
