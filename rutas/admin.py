from django.contrib.gis import admin
from rutas.models import *
import floppyforms as forms
from django.forms import ModelForm, Textarea
from django.contrib.admin import ModelAdmin
from usuarios.models import Usuario
from django.db.models import Q
try:
	import json
except:
	import django.utils.simplejson as json

class GMapPointWidget(forms.gis.BaseGMapWidget, forms.gis.PointWidget):
	pass

class GMapLineStringWidget(forms.gis.BaseGMapWidget, forms.gis.LineStringWidget):
	pass

class PointForm(ModelForm):
	class Meta:
		fields = '__all__'
		widgets = {
            'the_geom': GMapPointWidget(),
        }

class LineStringForm(ModelForm):
	class Meta:
		fields = '__all__'
		widgets = {
            'the_geom': GMapLineStringWidget(),
        }

class EventoRutaAdmin(ModelAdmin):
	form=PointForm

	def save_model(self, request, obj, form, change):
		obj.save()
		usuarios=Usuario.objects.all()
		data = {}
		data['comentario'] = obj.comentario
		data['lat']=str(obj.the_geom.y)
		data['lon']=str(obj.the_geom.x)
		data['tipo']=str(obj.tipo)
		for i in usuarios:
			i.dispositivo.send_message({'msg':str(json.dumps(data))})

class EstacionDeServicioAdmin(ModelAdmin):
	form=PointForm

class RutaAdmin(ModelAdmin):
	form=LineStringForm

class VerticeAdmin(ModelAdmin):
	form=PointForm

admin.site.register(RutasTunja, RutaAdmin)
admin.site.register(RutasTunjaVerticesPgr, VerticeAdmin)
admin.site.register(EventoRuta, EventoRutaAdmin)
admin.site.register(EstacionDeServicio, EstacionDeServicioAdmin)