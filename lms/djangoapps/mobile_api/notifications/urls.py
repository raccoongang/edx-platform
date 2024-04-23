from django.urls import path
from .views import GCMDeviceAuthorizedViewSet


CREATE_GCM_DEVICE = GCMDeviceAuthorizedViewSet.as_view({'post': 'create'})


urlpatterns = [
    path('create-token/', CREATE_GCM_DEVICE, name='gcmdevice-list'),
]
