from django.urls import path
from rest_framework.routers import DefaultRouter

from modules.planning.views import ProjectionView, PurchaseIntentionViewSet

router = DefaultRouter()
router.register(r"intentions", PurchaseIntentionViewSet, basename="intentions")

urlpatterns = [
    path("projection/", ProjectionView.as_view(), name="projection"),
] + router.urls
