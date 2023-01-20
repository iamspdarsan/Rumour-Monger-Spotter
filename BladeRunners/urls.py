from django.contrib import admin
from django.urls import path
from prodx import views

urlpatterns = [
    path('',views.Prodx.main_page),
    path('getlink',views.Prodx.getlink),
]
