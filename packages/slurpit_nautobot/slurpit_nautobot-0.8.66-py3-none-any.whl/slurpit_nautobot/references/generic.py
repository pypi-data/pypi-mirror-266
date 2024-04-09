from . import base_name, plugin_type
from .imports import *

from .. import get_config
from ..models import  SlurpitStagedDevice, ensure_slurpit_tags

def create_form(form, data, model, initial):
    return form(model, data, initial=initial)

def get_form_device_data(form):
    return {            
            'location': form.cleaned_data['location'],
            'rack': form.cleaned_data['rack'],
            'role': form.cleaned_data['role'],
            'position': form.cleaned_data['position'],
            'tenant': form.cleaned_data['tenant'],
        }

def set_device_custom_fields(device, fields):
    for k, v in fields.items():
        device._custom_field_data[k] = v

def get_default_objects():
    return {
        'device_type': DeviceType.objects.get(**get_config('DeviceType')),
    }

def status_inventory():
    return Status.objects.get_for_model(Device).get(name="Inventory")

def status_offline():
    return Status.objects.get_for_model(Device).get(name="Offline")

def get_create_dcim_objects(staged: SlurpitStagedDevice):
    manu, new = Manufacturer.objects.get_or_create(name=staged.brand)
    platform, new = Platform.objects.get_or_create(name=staged.device_os)
    dtype, new = DeviceType.objects.get_or_create(model=staged.device_type, manufacturer=manu)
    if new:
        ensure_slurpit_tags(dtype)
    return dtype

class SlurpitViewMixim(generic.ObjectListView):

    slurpit_data = {
            'plugin_type': plugin_type,
            'base_name': base_name,
            'plugin_base_name': f"plugins:{base_name}",
            'version': get_config('version'),
    }
    
    def extra_context(self):
        return {**self.slurpit_data, **self.slurpit_extra_context()}

    def slurpit_extra_context(self):
        return {}

class SlurpitViewSet(NautobotModelViewSet):
    pass

class SlurpitQuerySetMixim(ConfigContextQuerySetMixin):
    pass