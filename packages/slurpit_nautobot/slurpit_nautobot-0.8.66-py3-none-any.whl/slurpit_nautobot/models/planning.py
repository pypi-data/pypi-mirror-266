from django.db import models
from nautobot.apps.models import PrimaryModel
from django.urls import reverse

class SlurpitPlanning(PrimaryModel):
    name = models.CharField(max_length=255, unique=True)
    planning_id = models.BigIntegerField(unique=True)
    selected = models.BooleanField(default=False)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}"
    
    def get_absolute_url(self):
        return reverse("plugins:slurpit_nautobot:slurpitplanning", args=[self.pk])

class SlurpitSnapshot(PrimaryModel):
    hostname = models.CharField(max_length=255)
    planning_id = models.BigIntegerField()
    content = models.JSONField()
    result_type = models.CharField(max_length=255, default="template_result")
    
    def __str__(self):
        return f"{self.hostname}#{self.planning_id}"