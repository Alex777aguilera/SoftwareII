from django.urls import path

from . import views

app_name = 'ecommerce_app'

urlpatterns = [
 path('', views.principal, name='principal'),
 path('principal/admin', views.principal_admin, name='principal_admin'),
 # path('principal/cliente', views.principal_cliente, name='principal_cliente'),
 path('login', views.login, name='login'),
<<<<<<< HEAD
 path('registro/cliente', views.registro_cliente, name="registro_cliente"),	
 path('modificar/cliente/', views.modificar_cliente, name="modificar_cliente"),
 path('modificar/cliente_normal/', views.modificar_normal, name="modificar_normal"),
=======
>>>>>>> f5094a2fb4a49a2aca81694752b4a723385991e1
 path('cerrar_sesion', views.cerrar_sesion, name='cerrar_sesion'),
 path('registrar_producto', views.registrar_producto, name='registrar_producto'),
 path('agregar/empresa', views.agregar_empresa, name='agregar_empresa'),
]