from django.contrib import admin 
from django.urls import path 
from django.conf import settings 
from django.conf.urls.static import static 
from . import views, url_handlers

urlpatterns = [
    path('uvod', views.uvod, name="uvod"),
    path('images', views.Obrazek.pg1, name="images"),
    path('logo', views.pg2, name="logo"),
    #path("upload/", views.Upload.as_view()),
    path('', url_handlers.index_handler),
]
