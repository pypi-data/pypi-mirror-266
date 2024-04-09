from django import forms
from nautobot.dcim.choices import DeviceStatusChoices, DeviceStatusChoices
# from nautobot.ipam.choices import IPRangeStatusChoices
from nautobot.dcim.models import DeviceType, Location, Rack, Device
from django.utils.translation import gettext_lazy as _
from nautobot.apps.api import ChoiceField
from nautobot.apps.forms import NautobotBulkEditForm
from nautobot.core.forms import add_blank_choice
from nautobot.core.forms.fields import DynamicModelChoiceField
from nautobot.core.forms.widgets import APISelect

from nautobot.tenancy.models import TenantGroup, Tenant
from nautobot.core.forms import BootstrapMixin
from .models import SlurpitImportedDevice, SlurpitPlanning, SlurpitSetting
from .management.choices import SlurpitApplianceTypeChoices
from nautobot.extras.models import CustomField, Status,Role
from django.contrib.contenttypes.models import ContentType
# from nautobot.ipam.models import IPRange
from nautobot.extras.models.tags import Tag


class OnboardingForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=SlurpitImportedDevice.objects.all(), widget=forms.MultipleHiddenInput())
    device_type = forms.ChoiceField(
        choices=[],
        label=_('Device type'),
        required=True
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=True,
        query_params={
            'site_id': '$site'
        },
        initial_params={
            'racks': '$rack'
        }
    )
    rack = DynamicModelChoiceField(
        label=_('Rack'),
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=True,
    )
    position = forms.DecimalField(
        label=_('Position'),
        required=False,
        help_text=_("The lowest-numbered unit occupied by the device"),
        localize=True,
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'disabled-indicator': 'device',
                'data-dynamic-params': '[{"fieldName":"face","queryParam":"face"}]'
            },
        )
    )
    # latitude = forms.DecimalField(
    #     label=_('Latitude'),
    #     max_digits=8,
    #     decimal_places=6,
    #     required=False,
    #     help_text=_("GPS coordinate in decimal format (xx.yyyyyy)")
    # )
    # longitude = forms.DecimalField(
    #     label=_('longitude'),
    #     max_digits=9,
    #     decimal_places=6,
    #     required=False,
    #     help_text=_("GPS coordinate in decimal format (xx.yyyyyy)")
    # )
    tenant_group = DynamicModelChoiceField(
        label=_('Tenant group'),
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={
            'tenants': '$tenant'
        }
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        query_params={
            'group_id': '$tenant_group'
        }
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    status = ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(DeviceStatusChoices),
        required=False
    )
    class Meta:
        model = SlurpitImportedDevice
        nullable_fields = [
            "description",
            "location",
            "tenant",
            "tenant_group",
            "status",
            # "latitude",
            # "longitude",
            "rack"
        ]
    def __init__(self, *args, **kwargs):
        device_types = kwargs['initial'].pop('device_types', None)
        super().__init__(*args, **kwargs)
        choices = []
        if device_types and len(device_types) > 1:
            choices = [('keep_original', 'Keep Original Type')]
        for dt in DeviceType.objects.all().order_by('id'):
            choices.append((dt.id, dt.model))          
        self.fields['device_type'].choices = choices

class SlurpitPlanningTableForm(BootstrapMixin, forms.Form):
    planning_id = DynamicModelChoiceField(
        queryset=SlurpitPlanning.objects.all(),
        to_field_name='planning_id',
        required=True,
        label=_("Slurpit Plans"),
    )

class SlurpitApplianceTypeForm(BootstrapMixin, forms.Form):
    model =  SlurpitSetting
    appliance_type = forms.ChoiceField(
        label=_('Data synchronization'),
        choices=add_blank_choice(SlurpitApplianceTypeChoices),
        required=False
    )

class SlurpitMappingForm(BootstrapMixin, forms.Form):
    source_field = forms.CharField(
        required=True,
        label=_("Source Field"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text=_("Slurpit Device's Field"),
    )
    
    target_field = forms.ChoiceField(
        choices=[
        ],
        required=True,
        label=f"Target Field",
    )
    
    
    def __init__(self, *args, **kwargs):
        choice_name = kwargs.pop('choice_name', None) 
        doaction = kwargs.pop('doaction', None) 
        mapping_type = kwargs.pop('mapping_type', None) 
        super(SlurpitMappingForm, self).__init__(*args, **kwargs)
        
        choices = []
        
        if mapping_type == "device":
            for field in Device._meta.get_fields():
                if not field.is_relation or field.one_to_one or (field.many_to_one and field.related_model):
                    choices.append((f'device|{field.name}', f'device | {field.name}'))
        
            # Add custom fields
            device = ContentType.objects.get(app_label='dcim', model='device')
            device_custom_fields = CustomField.objects.filter(content_types=device)

            for custom_field in device_custom_fields:
                choices.append((f'device|cf_{custom_field.key}', f'device | {custom_field.key}'))
        else:
            pass
            # for field in IPRange._meta.get_fields():
            #     if not field.is_relation or field.one_to_one or (field.many_to_one and field.related_model):
            #         choices.append((f'iprange|{field.name}', f'iprange | {field.name}'))
        
        self.fields[f'target_field'].choices = choices

        if doaction != "add":
            self.fields[f'target_field'].label = choice_name
            del self.fields[f'source_field']


class SlurpitDeviceForm(BootstrapMixin, forms.Form):
    mapping_item = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label=_("Device"),
    )

class SlurpitDeviceStatusForm(BootstrapMixin, forms.Form):
    management_status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(DeviceStatusChoices),
        required=False
    )

# class SlurpitIPRangeStatusForm(BootstrapMixin, forms.Form):
#     management_status = forms.ChoiceField(
#         label=_('Status'),
#         choices=add_blank_choice(IPRangeStatusChoices),
#         required=False
#     )

# class SlurpitIPRangeForm(BootstrapMixin, forms.Form):
#     mapping_item = DynamicModelChoiceField(
#         queryset=IPRange.objects.all(),
#         required=True,
#         label=_("IP Range"),
#     )

#     def __init__(self, *args, **kwargs):
#         super(SlurpitIPRangeForm, self).__init__(*args, **kwargs)
#         slurpit_tag = Tag.objects.get(name="slurpit")
#         self.fields['mapping_item'].queryset = IPRange.objects.filter(tags__in=[slurpit_tag])