from django.urls import path

from .views.file import ImportFileViewSet, FileDownloadViewSet, FileUploadViewSet, FileConfirmViewSet
from ..api.routers import OptionalSlashRouter

router = OptionalSlashRouter()
router.register('files', ImportFileViewSet, 'files')

urlpatterns = [
    path('files/<pk>/download/', FileDownloadViewSet.as_view(), name='download'),
    path('files/upload/', FileUploadViewSet.as_view(), name='upload'),
    path('files/<pk>/confirm/', FileConfirmViewSet.as_view(), name='confirm'),
]

urlpatterns += router.urls
