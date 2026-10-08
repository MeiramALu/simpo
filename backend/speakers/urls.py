from django.urls import path

from . import views

urlpatterns = [
    path('', views.speakers, name='speakers-list'),
    path('<int:pk>/photo/', views.speaker_photo, name='speaker-photo'),
]
