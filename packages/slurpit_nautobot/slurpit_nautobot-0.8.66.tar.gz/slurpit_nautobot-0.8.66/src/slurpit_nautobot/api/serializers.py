from nautobot.core.api import NautobotModelSerializer
from rest_framework import serializers

from slurpit_nautobot.models import SlurpitPlanning, SlurpitImportedDevice, SlurpitStagedDevice, SlurpitLog, SlurpitSetting, SlurpitSnapshot, SlurpitMapping

__all__ = (
    'SlurpitPlanningSerializer',
    'SlurpitStagedDeviceSerializer',
    'SlurpitImportedDeviceSerializer',
    'SlurpitLogSerializer',
    'SlurpitSettingSerializer',
    'SlurpitSnapshotSerializer'
)

class SlurpitPlanningSerializer(NautobotModelSerializer):
    id = serializers.IntegerField(source='planning_id')
    comment = serializers.CharField(source='comments')

    class Meta:
        model = SlurpitPlanning
        fields = ['id', "name", "comment", "display"]

class SlurpitStagedDeviceSerializer(NautobotModelSerializer):
    id = serializers.IntegerField(source='slurpit_id')
    class Meta:
        model = SlurpitStagedDevice
        fields = ['id', 'disabled', 'hostname', 'fqdn', 'ipv4', 'device_os', 'device_type', 'brand', 'createddate', 'changeddate']

class SlurpitSnapshotSerializer(NautobotModelSerializer):
    class Meta:
        model = SlurpitSnapshot
        fields = '__all__'


class SlurpitImportedDeviceSerializer(NautobotModelSerializer):
    id = serializers.IntegerField(source='slurpit_id')
    class Meta:
        model = SlurpitImportedDevice
        fields = ['id', 'disabled', 'hostname', 'fqdn', 'ipv4', 'device_os', 'device_type', 'brand', 'createddate', 'changeddate']

class SlurpitLogSerializer(NautobotModelSerializer):
    class Meta:
        model = SlurpitLog
        fields = '__all__'

class SlurpitSettingSerializer(NautobotModelSerializer):
    class Meta:
        model = SlurpitSetting
        fields = ['server_url', 'api_key', 'last_synced', 'connection_status', 'push_api_key', 'appliance_type']

class SlurpitMappingSerializer(NautobotModelSerializer):
    class Meta:
        model = SlurpitMapping
        fields = ['source_field', 'target_field', 'mapping_type']