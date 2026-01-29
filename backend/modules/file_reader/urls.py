from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.file_reader.views import BillViewSet, UploadFileView

router = DefaultRouter()
router.register(r"bills", BillViewSet, basename="bill")

urlpatterns = [
    path("upload/", UploadFileView.as_view(), name="upload_file"),
    path("", include(router.urls)),
]
