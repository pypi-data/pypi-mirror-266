from nautobot.core.api.routers import OrderedDefaultRouter
from . import views

router = OrderedDefaultRouter()
router.APIRootView = views.SlurpitRootView
router.register("planning", views.SlurpitPlanningViewSet)
router.register("planning-data", views.SlurpitSnapshotViewSet)
router.register("device", views.DeviceViewSet)
router.register("test", views.SlurpitTestAPIView)
router.register("nautobot-device", views.SlurpitDeviceView)
app_name = 'slurpit-api'
urlpatterns = router.urls
