from rest_framework.routers import DefaultRouter

from modules.planning.views import PurchaseIntentionViewSet

router = DefaultRouter()
router.register(r"intentions", PurchaseIntentionViewSet, basename="intentions")

urlpatterns = router.urls
