# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rutas', '0003_auto_20160204_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventoruta',
            name='activo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='eventoruta',
            name='comentario',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='eventoruta',
            name='the_geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='eventoruta',
            name='tipo',
            field=models.CharField(default='A', max_length=1, choices=[(b'A', b'Accidente'), (b'C', b'Cierre'), (b'M', b'Mantenimiento')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventoruta',
            name='verificado',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='eventoruta',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
