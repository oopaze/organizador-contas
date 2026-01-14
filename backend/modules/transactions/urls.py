from rest_framework.routers import DefaultRouter

from modules.transactions.views import ActorViewSet, TransactionViewSet, SubTransactionViewSet

router = DefaultRouter()
router.register(r"actors", ActorViewSet, basename="actors")
router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"sub_transactions", SubTransactionViewSet, basename="sub_transactions")

urlpatterns = router.urls
