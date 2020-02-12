from django.contrib import admin
from django.forms import ModelForm
from floppyforms.gis import PointWidget, BaseGMapWidget
from .models import *

# Register your models here.


class CustomPointWidget(PointWidget, BaseGMapWidget):
    class Media:
        js = ('js/openlayers/OpenLayers.js',
              'https://maps.google.com/maps/api/js?v=3&sensor=false',
              'floppyforms/js/MapWidget.js')
        css = {
            'all': ('css/openLayers/style.css',)
        }


class AgentAdminForm(ModelForm):
    class Meta:
        model = Agent
        fields = ('user', 'location', 'is_active')
        widgets = {
            'location': CustomPointWidget()
        }


class AgentAdmin(admin.ModelAdmin):
    form = AgentAdminForm


admin.site.register(Agent, AgentAdmin)
