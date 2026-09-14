from rest_framework.routers import DefaultRouter

from modules.cards.views import CardViewSet

router = DefaultRouter()
router.register(r"cards", CardViewSet, basename="cards")

urlpatterns = router.urls
