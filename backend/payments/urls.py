from django.urls import path

from . import views

urlpatterns = [
    path('', views.PaymentListCreateView.as_view(), name='payment-list'),
    path('providers/', views.ProvidersView.as_view(), name='payment-providers'),
    path('<uuid:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<uuid:pk>/receipt/', views.PaymentReceiptView.as_view(), name='payment-receipt'),
    path('<uuid:pk>/cancel/', views.PaymentCancelView.as_view(), name='payment-cancel'),
    path('webhook/<str:provider>/', views.webhook, name='payment-webhook'),
    path('test-checkout/<uuid:pk>/', views.test_checkout, name='payment-test-checkout'),
]
