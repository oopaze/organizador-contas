from rest_framework.routers import DefaultRouter

from modules.loans.views import LoanViewSet, LoanPaymentViewSet

router = DefaultRouter()
router.register(r"loans", LoanViewSet, basename="loans")
router.register(r"loan_payments", LoanPaymentViewSet, basename="loan_payments")

urlpatterns = router.urls
