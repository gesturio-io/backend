from django.contrib import admin
from django.urls import path, include
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('', views.index, name='index'),
    path('video/', include('videoSocket.urls')),
]
