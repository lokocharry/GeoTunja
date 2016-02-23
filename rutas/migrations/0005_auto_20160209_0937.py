# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rutas', '0004_auto_20160204_0936'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstacionDeServicio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
                ('precio_gasolina', models.IntegerField()),
                ('precio_acpm', models.IntegerField()),
                ('precio_gas', models.IntegerField()),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='eventoruta',
            options={'managed': False},
        ),
    ]
