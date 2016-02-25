from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from gcm.models import Device

from django.utils import timezone

class Usuario(models.Model):
	usuario = models.OneToOneField(User, on_delete=models.CASCADE)
	dispositivo = models.ForeignKey(Device)

	def __unicode__(self):
		if self.usuario.get_full_name()=="":
			return "%s" % (self.usuario.email)
		else:
			return "%s" % (self.usuario.get_full_name())