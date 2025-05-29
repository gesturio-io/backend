from django.contrib import admin
from django.urls import path, include
from users import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('', views.index, name='index'),
    path('learn/',include('learn.urls')),
    path('settings/', include('settings.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
