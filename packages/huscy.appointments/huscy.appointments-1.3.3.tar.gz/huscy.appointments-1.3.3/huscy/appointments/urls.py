from django.urls import include, path
from rest_framework.routers import DefaultRouter

from huscy.appointments import views
from huscy.appointments.feed import AppointmentFeed
from huscy.appointments.feed import get_feed_url


router = DefaultRouter()
router.register('appointments', views.AppointmentsViewSet, basename='appointment')
router.register('resources', views.ResourcesViewSet)


urlpatterns = [
    path('api/', include(router.urls)),

    path('appointments/feed/<str:token>', AppointmentFeed(), name='feed'),
    path('appointments/feedurl/', get_feed_url, name='feed-url'),
]
