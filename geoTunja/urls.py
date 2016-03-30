"""geoTunja URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib.gis import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('gcm.urls')),
    url(r'^rutas/', 'rutas.views.calcularRuta', name='rutas'),
    url(r'^rutasAlt/', 'rutas.views.calcularRutaAlterna', name='rutaAlt'),
    url(r'^nombreRuta/', 'rutas.views.obtenerNombreRuta', name='rutas'),
    url(r'^alertas/', 'rutas.views.obtenerAlertas', name='alertas'),
    url(r'^alertasVerificadas/', 'rutas.views.obtenerAlertasVerificadas', name='alertasVerificadas'),
    url(r'^crearAlerta/', 'rutas.views.crearAlerta', name='crearAlerta'),
    url(r'^estaciones/', 'rutas.views.obtenerEstacionesDeServicio', name='obtenerEstacionesDeServicio'),
    url(r'^votarEventoUp/', 'rutas.views.votarEventoUp', name='votarEventoUp'),
    url(r'^votarEventoDown/', 'rutas.views.votarEventoDown', name='votarEventoDown'),
    url(r'^ingresar/', 'rutas.views.ingresar', name='ingresar'),
    url(r'^obtenerDirecciones/', 'rutas.views.obtenerDirecciones', name='obtenerDirecciones'),
    url(r'^obtenerDireccionesDeVerdad/', 'rutas.views.obtenerDireccionesDeVerdad', name='obtenerDireccionesDeVerdad'),
]
