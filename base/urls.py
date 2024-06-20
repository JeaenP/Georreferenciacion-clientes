from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.clients, name='clients'),
    path('locations/', views.locations, name='locations'),
    path('clients/', views.clients, name='clients'),
    path('routes/', views.routes, name='routes'),
    path('registrar_visita/', views.registrar_visita, name='registrar_visita'),
    path('visits/', views.visits, name='visits')
]

