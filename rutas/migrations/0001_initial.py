# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventoRuta',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('activo', models.BooleanField(default=False)),
                ('verificado', models.BooleanField(default=False)),
                ('comentario', models.CharField(max_length=200, null=True, blank=True)),
                ('tipo', models.CharField(max_length=1, choices=[(b'A', b'Accidente'), (b'C', b'Cierre'), (b'M', b'Mantenimiento')])),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'db_table': 'evento_ruta',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RutasTunja',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('osm_id', models.BigIntegerField(null=True, blank=True)),
                ('osm_name', models.CharField(max_length=100, null=True, blank=True)),
                ('km', models.FloatField(null=True, blank=True)),
                ('kmh', models.IntegerField(null=True, blank=True)),
                ('cost', models.FloatField(null=True, blank=True)),
                ('reverse_cost', models.FloatField(null=True, blank=True)),
                ('x1', models.FloatField(null=True, blank=True)),
                ('y1', models.FloatField(null=True, blank=True)),
                ('x2', models.FloatField(null=True, blank=True)),
                ('y2', models.FloatField(null=True, blank=True)),
                ('the_geom', django.contrib.gis.db.models.fields.LineStringField(srid=4326, null=True, blank=True)),
                ('source', models.IntegerField(null=True, blank=True)),
                ('target', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'rutas_tunja',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RutasTunjaVerticesPgr',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('cnt', models.IntegerField(null=True, blank=True)),
                ('chk', models.IntegerField(null=True, blank=True)),
                ('ein', models.IntegerField(null=True, blank=True)),
                ('eout', models.IntegerField(null=True, blank=True)),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
            options={
                'db_table': 'rutas_tunja_vertices_pgr',
                'managed': True,
            },
        ),
    ]
