from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Al-Farabi Global Symposium 2026'
admin.site.site_title = 'AFGS 2026'
admin.site.index_title = 'Администрирование'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/registrations/', include('registrations.urls')),
    path('api/papers/', include('papers.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/speakers/', include('speakers.urls')),
    path('api/', include('program.urls')),
    path('api/meta/', include('frontend.api_urls')),
    path('', include('frontend.urls')),
]
