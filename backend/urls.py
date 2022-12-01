
from django.contrib import admin
from django.urls import path

from backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('view/', views.index, name='index'),

]
