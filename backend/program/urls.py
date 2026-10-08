from django.urls import path

from . import views

urlpatterns = [
    path('program/', views.program, name='program'),
    path('documents/<str:kind>/', views.document, name='document'),
]
