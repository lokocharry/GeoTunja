from django.contrib.gis import admin
from rutas.models import *
import floppyforms as forms
from django.forms import ModelForm, Textarea
from django.contrib.admin import ModelAdmin

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