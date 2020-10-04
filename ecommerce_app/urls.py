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
 path('ajax/marcas', views.ajax_categoria_marca, name='ajax_categoria_marca'),
 path('detalle/producto/<int:id_producto>/', views.detalle_producto, name='detalle_producto'),
 path('lista/categorias/', views.lista_categorias, name='lista_categorias'),



]