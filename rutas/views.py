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
from usuarios.models import Usuario
from django.db.models import Q

#SELECT st_asgeojson(the_geom), ST_Distance(ST_GeomFromText('POINT(-114.053205 51.069644)',4326),the_geom) AS distance
#FROM rutas_tunja ORDER BY distance ASC LIMIT 1;

from gcm.signals import device_registered
from usuarios.models import Usuario
try:
	import json
except:
	import django.utils.simplejson as json

import math
class Point(object):
    '''Creates a point on a coordinate plane with values x and y.'''

    COUNT = 0

    def __init__(self, x, y, nombre):
        '''Defines x and y variables'''
        self.X = x
        self.Y = y
        self.nombre = nombre

    def __str__(self):
        return "Point(%s,%s)"%(self.X, self.Y) 

    def getX(self):
        return self.X

    def getY(self):
        return self.Y

    def rotate90(self):
    	aux1=self.X
    	aux2=self.Y
    	self.X=-aux2
    	self.Y=aux1

    def rotateInverse90(self):
    	aux1=self.X
    	aux2=self.Y
    	self.X=aux2
    	self.Y=-aux1

    def rotate180(self):
    	aux1=self.X
    	aux2=self.Y
    	self.X=-aux1
    	self.Y=-aux2

    def rotateAngle(self, teta):
    	self.X=(self.X*math.cos(math.radians(teta)))-(self.Y*math.sin(math.radians(teta)))
    	self.Y=(self.X*math.sin(math.radians(teta)))+(self.Y*math.cos(math.radians(teta)))

def angle(pointA, pointB):
	from math import atan2, degrees, pi
	dx = pointB.X - pointA.X
	dy = pointB.Y - pointA.Y
	angle_rad = atan2(dy,dx)
	angle_deg = angle_rad*180.0/pi
	if angle_deg<0:
		angle_deg+=360
	return angle_deg

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
		cursor.execute("SELECT st_asgeojson(the_geom), km*1000 as distancia, kmh as velocidad FROM pgr_dijkstra('SELECT a.id, source, target, km as cost, reverse_cost, x1, y1, x2, y2  FROM rutas_tunja as a LEFT JOIN (SELECT EXTRACT(EPOCH FROM (fecha+(duracion|| time_format)::interval-NOW())) as diferencia, nn(the_geom, 2, 2, 2) as id FROM evento_ruta GROUP BY diferencia, the_geom HAVING EXTRACT(EPOCH FROM (fecha+(duracion || time_format)::interval -NOW()))>0) as b ON a.id = b.id WHERE b.id IS NULL GROUP BY a.id', %d, %d, true, true) as c, rutas_tunja as d WHERE id=id2;" % (origen, destino))
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

import ast
def obtenerDireccionesDeVerdad(request):
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
		cursor.execute("SELECT id, st_asgeojson(the_geom), osm_name FROM pgr_dijkstra('SELECT id, source, target, cost, reverse_cost FROM rutas_tunja', %d, %d, true, true ), rutas_tunja where id=id2;" % (origen, destino))
		ruta=cursor.fetchall()
		data=list(ruta)
		puntos=[]
		for i in data:
			pointA=ast.literal_eval(i[1])
			lat=pointA["coordinates"][0][0]
			lon=pointA["coordinates"][0][1]
			nombre=i[2]
			punto1=Point(lat, lon, nombre)
			puntos.append(punto1);
		orilat = float(request.GET.get('orilat'))
		orilon = float(request.GET.get('orilon'))
		yo=Point(orilat, orilon, "yo")
		pinit=puntos[1]
		angulo=angle(yo, pinit)
		if (angulo<=90 and angulo>=0) or (angulo>=270 and angulo<=360):
			if angulo<=45 or angulo>=315:
				print "Derecha"
				for i in puntos:
					i.rotateAngle(90-angulo)

		if angulo>=90 and angulo<=270:
			if angulo>=135 and angulo<=225:
				print "Izquierda"
				for i in puntos:
					i.rotateAngle(90-angulo)

		if angulo>225 and angulo<315:
			print "Atras"
			for i in puntos:
				i.rotateAngle(90-angulo)

		print "Me toca girar: "+str(angulo)

		response_dict = {}
		for index, i in enumerate(puntos, -1):
			p1=puntos[index]
			p2=puntos[index+1]
			angulo=angle(p1, p2)
			print angulo
			if (angulo<=90 and angulo>=0) or (angulo>=270 and angulo<=360):
				response_dict.update({str(index): "A la Derecha en "+p1.nombre})
				print "A la Derecha en "+p1.nombre
				for i in puntos:
					i.rotateAngle(angulo)

			if angulo>=90 and angulo<=270:
				response_dict.update({str(index): "A la Izquierda en "+p1.nombre})
				print "A la Izquierda en "+p1.nombre
				for i in puntos:
					i.rotateAngle(angulo)

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
		consulta= "SELECT st_asgeojson(the_geom), tipo, comentario, a.id, CASE WHEN a.id=b.object_id THEN count(object_id) ELSE 0 END as votos FROM evento_ruta a, vote_vote b GROUP BY object_id, tipo, comentario, a.id, the_geom, fecha, duracion, time_format HAVING EXTRACT(EPOCH FROM (fecha+(duracion || time_format)::interval -NOW()))>0"
		cursor.execute(consulta)
		alertas=cursor.fetchall()
		return HttpResponse(json.dumps(alertas), content_type='application/json')

def obtenerAlertasVerificadas(request):
	if request.method == "GET":
		cursor = connection.cursor()
		consulta= "SELECT st_asgeojson(the_geom), tipo, comentario, a.id, count(object_id) as votos FROM evento_ruta a, vote_vote b WHERE a.id=b.object_id GROUP BY object_id, tipo, comentario, a.id, the_geom HAVING count(object_id)>=1 AND EXTRACT(EPOCH FROM (fecha+(duracion || time_format)::interval -NOW()))>0;"
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
			print request.POST['email']
			evento.save()
			response_dict.update({'mensage': 'Creado exitoso'})
			usuarios=Usuario.objects.filter(~Q(usuario__email=request.POST['email']))
			data = {}
			data['comentario'] = evento.comentario
			data['lat']=str(evento.the_geom.y)
			data['lon']=str(evento.the_geom.x)
			data['tipo']=str(evento.tipo)
			for i in usuarios:
				i.dispositivo.send_message({'msg':str(json.dumps(data))})
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
