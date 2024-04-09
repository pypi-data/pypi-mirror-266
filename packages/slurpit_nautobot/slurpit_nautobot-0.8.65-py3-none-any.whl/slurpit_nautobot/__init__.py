import os

from django.apps import apps
from django.db.models.signals import post_migrate
from nautobot.apps import NautobotAppConfig
from nautobot.apps import config as app_config

class SlurpitConfig(NautobotAppConfig):
    name = "slurpit_nautobot"
    verbose_name = "Slurp'it Plugin"
    description = "Sync Slurp'it into Nautobot"
    version = '0.8.65'
    base_url = "slurpit"   
    default_settings = {
        'DeviceType': {'model': "Slurp'it"},
        'Role': {'name': "Slurp'it"},
        'Location': {'name': 'Slurp\'it'},
        'LocationType': {'name': 'Slurp\'it'},
        'Region': {'name': 'Slurp\'it'},
        'Tenant': {'name': 'Slurp\'it'},
        'Rack': {'name': 'Slurp\'it'},
        'ConfigTemplate': {'name': 'Slurp\'it'},
        'Manufacturer': {'name': 'OEM'},
        'unattended_import': False,
        'version': version
    }
    searchable_models = ["slurpitimporteddevice"]

    def ready(self):
        from .models import post_migration
        deps_app = apps.get_app_config("virtualization")
        post_migrate.connect(post_migration, sender=deps_app, weak=False)
        super().ready()


config = SlurpitConfig


def get_config(cfg):
    return app_config.get_app_settings_or_config(get_config.__module__, cfg)

