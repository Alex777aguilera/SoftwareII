from django.urls import path

from . import views

app_name = 'ecommerce_app'

urlpatterns = [
 path('', views.principal, name='principal'),
 path('principal/admin', views.principal_admin, name='principal_admin'),
 # path('principal/cliente', views.principal_cliente, name='principal_cliente'),
 path('login', views.login, name='login'),
 path('registro/cliente', views.registro_cliente, name="registro_cliente"),	
 path('modificar/cliente/', views.modificar_cliente, name="modificar_cliente"),
 path('modificar/cliente_normal/', views.modificar_normal, name="modificar_normal"),
 path('cerrar_sesion', views.cerrar_sesion, name='cerrar_sesion'),
 path('registrar/producto', views.registrar_producto, name='registrar_producto'),
 path('agregar/empresa', views.agregar_empresa, name='agregar_empresa'),
 path('agregar/categoria/producto', views.agregar_categoria, name='agregar_categoria'),
 path('agregar/categoria/genero', views.agregar_categoria_genero, name='agregar_categoria_genero'),
 path('agregar/marca', views.agregar_marca, name='agregar_marca'),
 path('ajax/marcas', views.ajax_categoria_marca, name='ajax_categoria_marca'),

]