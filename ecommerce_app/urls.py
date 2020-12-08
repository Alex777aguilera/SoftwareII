from django.urls import path, include
from django.conf import settings
from . import views

app_name = 'ecommerce_app'

urlpatterns = [
 path('', views.principal, name='principal'),
 path('principal/admin', views.principal_admin, name='principal_admin'),
 ## Social 
 # path('accounts/', include('django.contrib.auth.urls')),
 # path('social-auth/', include('social_django.urls', namespace='social')),
 
 ##
 path('login', views.login, name='login'),
 path('registro/cliente', views.registro_cliente, name="registro_cliente"),	
 path('modificar/cliente/<int:id_cliente>/', views.modificar_cliente, name="modificar_cliente"),
 path('modificar/cliente_normal/', views.modificar_normal, name="modificar_normal"),
 path('cerrar_sesion', views.cerrar_sesion, name='cerrar_sesion'),
 path('registrar/producto', views.registrar_producto, name='registrar_producto'),
 path('agregar/empresa', views.agregar_empresa, name='agregar_empresa'),
 path('carrito', views.carrito, name='carrito'),
 path('agregar/categoria', views.agregar_categoria, name='agregar_categoria'),
 path('modificar/categoria/<int:id_categoria>/', views.modificar_categoria, name='modificar_categoria'),
 path('agregar/genero', views.agregar_genero, name='agregar_genero'),
 path('modificar/genero/<int:id_genero>/', views.modificar_genero, name='modificar_genero'),
 path('agregar/marca', views.agregar_marca, name='agregar_marca'),
 path('modificar/marca/<int:id_marca>/', views.modificar_marca, name='modificar_marca'),
 path('ajax/categoria/subcategorias', views.ajax_categoria_subcategoria, name='ajax_categoria_subcategoria'),
 path('detalle/producto/<int:id_producto>/', views.detalle_producto, name='detalle_producto'),
 path('lista/categorias/', views.lista_categorias, name='lista_categorias'),
 path('ajax/subcategoria/marcas', views.ajax_subcategoria_marca, name='ajax_subcategoria_marca'),
 path('modificar/imagen/producto<int:id_producto>/', views.modificar_img_producto, name='modificar_img_producto'),
 path('modificar/producto/<int:id_producto>/', views.modificar_producto, name='modificar_producto'),
 path('delete/prudcto/carrito/<int:id_Pdelete>/', views.Eliminar_producto_carrito, name='Eliminar_producto_carrito'),
 path('productos/categoria/<int:idcategoria>/', views.productos_categoria, name='productos_categoria'),
 path('ajax/existencia', views.ajax_existencia, name='ajax_existencia'),
 path('registro/lote', views.registrar_lote, name='registrar_lote'),
 path('email', views.email, name='email'),
 path('perfil/cliente', views.perfil_cliente, name='perfil_cliente'),
 path('modificar/imagen/cliente/<int:id_cliente>/', views.modificar_img_cliente, name='modificar_img_cliente'),
 path('modificar/domicilio/<int:id_domicilio>/', views.modificar_domicilio, name='modificar_domicilio'),
 path('aregar/subcategoria', views.agregar_subcategoria, name='agregar_subcategoria'),
 path('modificar/subcategoria/<int:id_subcategoria>/', views.modificar_subcategoria, name='modificar_subcategoria'),
 path('datos/clientes', views.datos_clientes_admin, name='datos_clientes_admin'),
 path('productos/categorias/<int:id_categoria>/', views.productos_categorias, name='productos_categorias'),
 path('productos/subcategoria/<int:id_categoria>,<int:id_subcategoria>/', views.productos_subcategoria, name='productos_subcategoria'),


]