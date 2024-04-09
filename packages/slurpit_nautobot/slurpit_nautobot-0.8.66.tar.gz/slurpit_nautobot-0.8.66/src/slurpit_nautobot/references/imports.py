from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.views import generic
from nautobot.core.forms.utils import restrict_form_fields
from nautobot.dcim.api.serializers import DeviceSerializer
from nautobot.dcim.choices import DeviceStatusChoices
from nautobot.dcim.filters import DeviceFilterSet
from nautobot.dcim.models import  Manufacturer, Platform, DeviceType, Device, Location, LocationType
from nautobot.extras.api.views import ConfigContextQuerySetMixin, NautobotModelViewSet
from nautobot.extras.models import CustomField, Status, Role
from nautobot.extras.models.tags import Tag
from nautobot.tenancy.models import Tenant
