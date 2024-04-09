from django.db import models
from nautobot.apps.models import PrimaryModel

class SlurpitMapping(PrimaryModel):
    source_field = models.CharField(max_length=255, unique=True)
    target_field = models.CharField(max_length=255)
    mapping_type = models.CharField(max_length=255, default="")

    def get_changelog_url(self):
        return '/'
    
    def __str__(self):
        return f"{self.source_field}"