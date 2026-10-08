from django.urls import path

from . import views

urlpatterns = [
    path('', views.RegistrationListCreateView.as_view(), name='registration-list'),
    path('<int:pk>/', views.RegistrationDetailView.as_view(), name='registration-detail'),
    path('<int:pk>/cancel/', views.RegistrationCancelView.as_view(), name='registration-cancel'),
]
