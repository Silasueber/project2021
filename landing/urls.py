from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landingView, name="landing"),
    path('who', views.whoFollowsWhoView, name="who"),
    path('shared', views.landingView, name="shared"),
    path('generate', views.generateDataView, name="generateData"),
    path('calculate', views.calculateView, name="calculateData"),
]
