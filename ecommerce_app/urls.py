from django.urls import path

from . import views

app_name = 'ecommerce_app'

urlpatterns = [
 path('', views.principal, name='principal'),
 path('login', views.login, name='login'),	
 path('cerrar_sesion', views.cerrar_sesion, name='cerrar_sesion'),
]