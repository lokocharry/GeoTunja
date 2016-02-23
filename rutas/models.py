from django.contrib.gis.db import models
from vote.managers import VotableManager

TIPO_EVENTO = (
   ('A', 'Accidente'),
   ('C', 'Cierre'),
   ('M', 'Mantenimiento'),
)

class RutasTunja(models.Model):
    id = models.AutoField(primary_key=True)
    osm_id = models.BigIntegerField(blank=True, null=True)
    osm_name = models.CharField(max_length=100, blank=True, null=True)
    km = models.FloatField(blank=True, null=True)
    kmh = models.IntegerField(blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    reverse_cost = models.FloatField(blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    the_geom = models.LineStringField(blank=True, null=True, srid=4326)
    source = models.IntegerField(blank=True, null=True)
    target = models.IntegerField(blank=True, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        if self.osm_name is None:
            return "Sin nombre"
        else:
            return self.osm_name
    class Meta:
        managed = True
        db_table = 'rutas_tunja'

class RutasTunjaVerticesPgr(models.Model):
    id = models.AutoField(primary_key=True)
    cnt = models.IntegerField(blank=True, null=True)
    chk = models.IntegerField(blank=True, null=True)
    ein = models.IntegerField(blank=True, null=True)
    eout = models.IntegerField(blank=True, null=True)
    the_geom = models.PointField(blank=True, null=True, srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return unicode(self.id)

    class Meta:
        managed = True
        db_table = 'rutas_tunja_vertices_pgr'

class EventoRuta(models.Model):
    id = models.AutoField(primary_key=True)
    activo = models.BooleanField(default=True)
    verificado = models.BooleanField(default=False)
    comentario = models.CharField(max_length=200, null=True, blank=True)
    tipo = models.CharField(max_length=1, choices=TIPO_EVENTO)
    the_geom = models.PointField(srid=4326, null=True, blank=True)
    objects = models.GeoManager()
    votos = VotableManager()

    class Meta:
        managed = True
        db_table = 'evento_ruta'

class EstacionDeServicio(models.Model):
    nombre=models.CharField(max_length=50)
    precio_gasolina = models.IntegerField()
    precio_acpm = models.IntegerField()
    precio_gas = models.IntegerField()
    the_geom = models.PointField(srid=4326, null=True, blank=True)
    objects = models.GeoManager()

    class Meta:
        managed = True
        db_table = 'estacion_de_servicio'