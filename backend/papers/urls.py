from django.urls import path

from . import views

urlpatterns = [
    path('', views.PaperListCreateView.as_view(), name='paper-list'),
    path('<int:pk>/', views.PaperDetailView.as_view(), name='paper-detail'),
    path('<int:pk>/withdraw/', views.PaperWithdrawView.as_view(), name='paper-withdraw'),
    path('<int:pk>/file/', views.PaperFileView.as_view(), name='paper-file'),
]
