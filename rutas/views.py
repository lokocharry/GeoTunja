from django.shortcuts import render
from django.db import connection
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import GEOSGeometry
from rutas.models import EventoRuta
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
import xmltodict, json

#SELECT st_asgeojson(the_geom), ST_Distance(ST_GeomFromText('POINT(-114.053205 51.069644)',4326),the_geom) AS distance
#FROM rutas_tunja ORDER BY distance ASC LIMIT 1;

from gcm.signals import device_registered
from django.contrib.auth.models import User
from usuarios.models import Usuario
try:
	import json
except:
	import django.utils.simplejson as json

def device_registered_handler(sender, **kwargs):
	request = kwargs['request']
	device = kwargs['device']
	body_unicode = request.body.decode('utf-8')
	body = json.loads(body_unicode)
	user = User.objects.create_user(username=body['email'], email=body['email'], password=body['password'])
	user.first_name=body['name']
	user.save()
	usuario = Usuario(usuario=user, dispositivo=device)
	usuario.save()
	print "asdtqywfehgdvasd"
device_registered.connect(device_registered_handler)


def calcularRuta(request):
	if request.method == "GET":
		orilat = request.GET.get('orilat')
		orilon = request.GET.get('orilon')
		deslat = request.GET.get('deslat')
		deslon = request.GET.get('deslon')
		cursor = connection.cursor()
		consulta= "SELECT id, ST_Distance(ST_SetSRID(ST_Point("+orilat+", "+orilon+"), 4326), the_geom) AS distance FROM rutas_tunja_vertices_pgr ORDER BY distance ASC LIMIT 1;"
		cursor.execute(consulta)
		origen=cursor.fetchone()[0]
		consulta= "SELECT id, ST_Distance(ST_SetSRID(ST_Point("+deslat+", "+deslon+"), 4326), the_geom) AS distance FROM rutas_tunja_vertices_pgr ORDER BY distance ASC LIMIT 1;"
		cursor.execute(consulta)
		destino=cursor.fetchone()[0]
		cursor.execute("SELECT st_asgeojson(the_geom) FROM pgr_dijkstra('SELECT id, source, target, cost, reverse_cost FROM rutas_tunja', %d, %d, true, true ), rutas_tunja where id=id2;" % (origen, destino))
		res=cursor.fetchall()
		return HttpResponse(json.dumps(res), content_type='application/json')

def calcularRutaAlterna(request):
	if request.method == "GET":
		orilat = request.GET.get('orilat')
		orilon = request.GET.get('orilon')
		deslat = request.GET.get('deslat')
		deslon = request.GET.get('deslon')
		cursor = connection.cursor()
		consulta= "SELECT id, ST_Distance(ST_SetSRID(ST_Point("+orilat+", "+orilon+"), 4326), the_geom) AS distance FROM rutas_tunja_vertices_pgr ORDER BY distance ASC LIMIT 1;"
		cursor.execute(consulta)
		origen=cursor.fetchone()[0]
		consulta= "SELECT id, ST_Distance(ST_SetSRID(ST_Point("+deslat+", "+deslon+"), 4326), the_geom) AS distance FROM rutas_tunja_vertices_pgr ORDER BY distance ASC LIMIT 1;"
		cursor.execute(consulta)
		destino=cursor.fetchone()[0]
		cursor.execute("SELECT st_asgeojson(the_geom) FROM pgr_astar('SELECT id, source, target, km as cost, reverse_cost, x1, y1, x2, y2 FROM rutas_tunja', %d, %d, true, true ), rutas_tunja where id=id2;" % (origen, destino))
		res=cursor.fetchall()
		return HttpResponse(json.dumps(res), content_type='application/json')

def obtenerDirecciones(request):
	response_dict = {}
	if request.method == "GET":	
		orilat = request.GET.get('orilat')
		orilon = request.GET.get('orilon')
		deslat = request.GET.get('deslat')
		deslon = request.GET.get('deslon')
		cursor = connection.cursor()
		consulta= "SELECT id, ST_Distance(ST_SetSRID(ST_Point("+orilat+", "+orilon+"), 4326), the_geom) AS distance FROM rutas_tunja_vertices_pgr ORDER BY distance ASC LIMIT 1;"
		cursor.execute(consulta)
		origen=cursor.fetchone()[0]
		consulta= "SELECT id, ST_Distance(ST_SetSRID(ST_Point("+deslat+", "+deslon+"), 4326), the_geom) AS distance FROM rutas_tunja_vertices_pgr ORDER BY distance ASC LIMIT 1;"
		cursor.execute(consulta)
		destino=cursor.fetchone()[0]
		cursor.execute("SELECT xml_directions(%d, %d, 'rutas_tunja');" % (origen, destino))
		x=str(cursor.fetchall())
		x.rstrip()
		y=BeautifulSoup(x)
		steps=y.directions.findAll("text")
		for idx, i in enumerate(steps):
			response_dict.update({str(idx): i.text})
		return HttpResponse(json.dumps(response_dict), content_type='application/json')

def obtenerNombreRuta(request):
	if request.method == "GET":
		lat = request.GET.get('lat')
		lon = request.GET.get('lon')
		cursor = connection.cursor()
		consulta= "SELECT id, osm_name, ST_Distance(ST_SetSRID(ST_Point("+lat+", "+lon+"), 4326), the_geom) AS distance FROM rutas_tunja ORDER BY distance ASC LIMIT 1;"
		cursor.execute(consulta)
		ruta=cursor.fetchall()
		print ruta
		return HttpResponse(json.dumps(ruta), content_type='application/json')

def obtenerAlertas(request):
	if request.method == "GET":
		cursor = connection.cursor()
		consulta= "SELECT st_asgeojson(the_geom), tipo, comentario, id FROM evento_ruta;"#Terminar consulta
		cursor.execute(consulta)
		alertas=cursor.fetchall()
		return HttpResponse(json.dumps(alertas), content_type='application/json')

def obtenerEstacionesDeServicio(request):
	if request.method == "GET":
		cursor = connection.cursor()
		consulta= "SELECT st_asgeojson(the_geom), nombre, precio_gasolina, precio_gas, precio_acpm FROM estacion_de_servicio;"
		cursor.execute(consulta)
		estaciones=cursor.fetchall()
		return HttpResponse(json.dumps(estaciones), content_type='application/json')

@csrf_exempt
def crearAlerta(request):
	response_dict = {}
	if request.method == "POST":
		try:
			evento=EventoRuta()
			lat=request.POST['lat']
			lon=request.POST['lon']
			pnt = GEOSGeometry('POINT(%s %s)' % (lon, lat))
			evento.the_geom=pnt
			evento.comentario=request.POST['comentario']
			evento.tipo=request.POST['tipo'][0]
			evento.duracion=request.POST['duracion']
			evento.save()
			response_dict.update({'mensage': 'Creado exitoso'})
		except Exception, e:
			print '%s (%s)' % (e.message, type(e))
		return HttpResponse(json.dumps(response_dict), content_type='application/json')

@csrf_exempt
def votarEventoUp(request):
	response_dict = {}
	if request.method == "POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			alerta=EventoRuta.objects.filter(id=request.POST['id'])[0]
			alerta.votos.up(user)
			response_dict.update({'mensage': 'Voto realizado'})
		except Exception, e:
			print '%s (%s)' % (e.message, type(e))
			response_dict.update({'mensage': 'Ya ha votado este evento'})
			return HttpResponse(json.dumps(response_dict), content_type='application/json')
		return HttpResponse(json.dumps(response_dict), content_type='application/json')

@csrf_exempt
def votarEventoDown(request):
	response_dict = {}
	if request.method == "POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			alerta=EventoRuta.objects.filter(id=request.POST['id'])[0]
			alerta.votos.down(user)
			response_dict.update({'mensage': 'Voto realizado'})
		except Exception, e:
			print '%s (%s)' % (e.message, type(e))
			response_dict.update({'mensage': 'Ya ha votado este evento'})
			return HttpResponse(json.dumps(response_dict), content_type='application/json')
		return HttpResponse(json.dumps(response_dict), content_type='application/json')

from django.contrib.auth import authenticate, login
@csrf_exempt
def ingresar(request):
	response_dict = {}
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			response_dict.update({'mensage': '200'})
			return HttpResponse(json.dumps(response_dict), content_type='application/json')
		else:
			response_dict.update({'mensage': '600'})
			return HttpResponse(json.dumps(response_dict), content_type='application/json')
	else:
		response_dict.update({'mensage': '700'})
		return HttpResponse(json.dumps(response_dict), content_type='application/json')
