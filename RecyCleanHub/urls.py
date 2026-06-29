from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from recycling.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('recycling/', include('recycling.urls')),
    path('payments/', include('payments.urls')),
    path('aggregators/', include('aggregators.urls')),
    path('recyclers/', include('recyclers.urls')),
    path('recycler/', include('recyclers.company_urls')),
    path('admin-panel/recyclers/', include('recyclers.admin_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)