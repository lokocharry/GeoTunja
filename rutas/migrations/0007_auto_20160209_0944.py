# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rutas', '0006_auto_20160209_0944'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='estaciondeservicio',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='eventoruta',
            options={'managed': True},
        ),
    ]
