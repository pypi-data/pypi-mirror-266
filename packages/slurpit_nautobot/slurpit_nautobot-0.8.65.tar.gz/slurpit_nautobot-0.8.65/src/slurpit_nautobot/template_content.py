# template_content.py
from django.urls import reverse
from nautobot.apps.ui import TemplateExtension

class DeviceExtraTabs(TemplateExtension):
    """Template extension to add extra tabs to the object detail tabs."""

    model = 'dcim.device'

    def detail_tabs(self):
        """
        You may define extra tabs to render on a model's detail page by utilizing this method.
        Each tab is defined as a dict in a list of dicts.

        For each of the tabs defined:
        - The <title> key's value will become the tab link's title.
        - The <url> key's value is used to render the HTML link for the tab

        These tabs will be visible (in this instance) on the Device model's detail page as
        set by the DeviceContent.model attribute "dcim.device"

        This example demonstrates defining two tabs. The tabs will be ordered by their position in list.
        """
        return [
            {
                "title": "Slurpit",
                "url": reverse("plugins:slurpit_nautobot:slurpit_planning", kwargs={"pk": self.context["object"].pk}),
                "weight": 50000
            }
        ]
    
template_extensions = [DeviceExtraTabs]
