from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='site-index'),
    path('map/', views.venue_map, name='venue-map'),
    path('favicon.ico', views.icon, {'name': 'favicon.ico'}),
    path('favicon.png', views.icon, {'name': 'favicon.png'}),
    path('apple-touch-icon.png', views.icon, {'name': 'apple-touch-icon.png'}),
]
