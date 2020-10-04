from django.shortcuts import render,redirect
from django.db import transaction,connections
from django.contrib.auth import login as auth_login,logout,authenticate
from django.http import HttpResponseRedirect,JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import *
from django.conf import settings
from django.db.models import Sum 
from django.db import transaction,connections #manejo de base de datos
import json, re, telegram, os 
from datetime import datetime
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password

from django.contrib.auth.decorators import login_required, permission_required

from ecommerce_app.models import *
# Create your views here.


#vista principal
def principal(request):
	productos = Producto.objects.all()
	categorias = Categoria.objects.all()
	data = {'productos':productos,'categorias':categorias}
	if request.user.is_authenticated:
		if request.user.is_superuser :
			return redirect('ecommerce_app:principal_admin')
		else:
			return render(request,'principal.html',data)
	else:
		return render(request,'principal.html',data)


## Vista admin
@login_required
def principal_admin(request):
	user = request.user
	print (user.pk)
	if user.is_authenticated:
		if request.user.is_superuser :
			return render(request,'inicio_admin.html')
		else:
			return redirect('ecommerce_app:principal')
			
		
	else:
		return render(request,'error.html')

# #vista cliente
# @login_required
# def principal_cliente(request):
# 	user = request.user
# 	if user.is_authenticated:
# 		if request.user.is_superuser :
# 			return redirect('ecommerce_app:principal_admin')
# 		else:
# 			return render(request,'inicio_cliente.html')
			
# 	else:
# 		return render(request,'error.html')

def login(request):
	if request.user.is_authenticated:
		if request.user.is_superuser :
			return redirect('ecommerce_app:principal_admin')
		else:
			return redirect('ecommerce_app:principal')	
		
	

	mensaje = ''
	if request.method == 'POST':
		username = request.POST.get('username')
		contrasenia = request.POST.get('pass')
		user = authenticate(username=username,password=contrasenia)
		
		if user is not None:
			if user.is_active:
				auth_login(request,user)
				if request.user.is_superuser :
					return redirect('ecommerce_app:principal_admin')
				else:
					return redirect('ecommerce_app:principal')	
	
			else:
				mensaje = 'USUARIO INACTIVO'
				return render(request,'login.html',{'mensaje':mensaje})
		else:
			mensaje = 'USUARIO O CONTRASEÑA INCORRECTO'
			return render(request,'login.html',{'mensaje':mensaje})


	return render(request,'login.html',{'mensaje':mensaje})



def cerrar_sesion(request):
	logout(request)
	return HttpResponseRedirect(reverse('ecommerce_app:login'))

def registro_cliente(request):
	guardar_modificar = True
	genero = Genero.objects.all()
	rango = 0
	username = ''
	lista_correo = []

	query_cliente, ret_data,errores = {},{},{}
	if request.method == 'POST':
		existe_usuario = False
		correo = request.POST.get('Correo')
		usuario = User.objects.filter(username=correo)

		ret_data['num_identidad'] = request.POST.get("identificacion")
		ret_data['nombres'] = request.POST.get("nombres")
		ret_data['apellidos'] = request.POST.get("apellidos")
		ret_data['genero'] = int(request.POST.get("genero"))
		ret_data['numero_telefono'] = request.POST.get("telefono")
		ret_data['fecha_nacimiento'] = request.POST.get("fecha_nacimiento")
		ret_data['correo'] = request.POST.get("Correo")
		email = request.POST.get('correo')

		
		if request.POST.get("identificacion") == '':
			errores['num_identidad'] = "DEBES INGRESAR LA IDENTIDAD"
		else:
			query_cliente["num_identidad"] = request.POST.get("identificacion")	
		if request.POST.get("nombres") == '':
			errores['nombres'] = "DEBES INGRESAR EL NOMBRE"
		else:
			query_cliente["nombres"] = request.POST.get("nombres")
		if request.POST.get("apellidos") == '':
			errores['apellidos'] = "DEBES INGRESAR EL APELLIDO"
		else:
			query_cliente["apellidos"] = request.POST.get("apellidos")
		if request.POST.get("fecha_nacimiento") == '':
			errores['fecha_nacimiento'] = "DEBES INGRESAR LA FECHA DE NACIMIENTO"
		else:
			query_cliente["fecha_nacimiento"] = request.POST.get("fecha_nacimiento")
		if request.POST.get("telefono") == '':
			errores['numero_telefono'] = "DEBES INGRESAR EL NUMERO"
		else:
			query_cliente["numero_telefono"] = request.POST.get("telefono")
		if request.POST.get("Correo") == '':
			errores['correo'] = "DEBES INGRESAR EL NUMERO"
		else:
			query_cliente["correo"] = request.POST.get("Correo")
			

		
	
		if request.POST.get("genero") == '':
			errores['genero'] = "DEBES SELECIONAR UN GENERO"
		else:
			query_cliente["genero"] = Genero.objects.get(pk=request.POST.get("genero"))
		
		query_cliente["imagen"] = request.FILES.get("imagen")

		password = BaseUserManager().make_random_password(7)
		lista_correo.append(correo)
		rango = correo.find('@') #Devulve la posicion donde esta el @
		for x in range(0,rango):
			username += correo[x]
			

		if not errores:
			try:
				#Creación de usuario
				User.objects.create_user(username, email, password)
				user = User.objects.last()
					



				query_cliente['usuario_cliente'] = user
				cliente = Cliente(**query_cliente)
				cliente.save()
			except Exception as e:
				print ("Entro aqui")
				transaction.rollback()
				errores['administrador'] = e 
				data = {'generos':genero,'ret_data':ret_data,
					'errores':errores,'guardar_modificar':guardar_modificar}
				return render(request,'registro_cliente.html',data)

			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:principal'))
		else:
			data = {'generos':genero,'ret_data':ret_data,
					'errores':errores,'guardar_modificar':guardar_modificar}
			return render(request,'registro_cliente.html',data)

	elif request.method	== 'GET':	
		data = {'generos':genero,'guardar_modificar':guardar_modificar}
		return render(request,'registro_cliente.html',data)
	
def modificar_cliente(request,id_cliente):
	clien = Cliente.objects.get(pk=id_cliente)
	ret_data,query_cliente,errores = {},{},{}
	if request.method=='POST':
		if request.POST.get('nombres') == '' or request.POST.get('apellidos') == '' or request.POST.get('num_identidad') == '' or request.POST.get('telefono') =='' or request.POST.get('fecha_nacimiento') ==''  or int(request.POST.get('genero')) == 0:
			errores['nombres'] = "HAY ERRORES!"
		if not errores:
			try: 
				clien = Cliente.objects.filter(pk=id_cliente).update(
																			 num_identidad = request.POST.get('num_identidad'),
																			 nombres = request.POST.get('nombres'),
																			 apellidos = request.POST.get('apellidos'),	
																			 telefono = request.POST.get('telefono'),																			 
																			 fecha_nacimiento = request.POST.get('fecha_nacimiento'),	
																			 imagen = request.FILES.get('imagen'),
																			 genero = request.POST.get('genero'),																			 
																			 ),
			except Exception as e:
				print (e)
				return HttpResponseRedirect(reverse('ecommerce_app:principal')+"?error")
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:principal'))		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:principal')+"?error")
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:principal'))

def modificar_normal(request,id_cliente):
	cliente = Cliente.objects.get(pk=id_cliente)
	generos = Genero.objects.all()
	guardar_modificar = False
	ret_data, errores = {},{}
	if request.method == 'POST':
		try:
			pass
		except Exception as e:
			cliente_q = Cliente.objects.filter(pk=id_cliente).update(num_identidad=request.POST.get('num_indentidad'),
																				nombres=request.POST.get('nombres'), 
																				apellidos=request.POST.get('apellidos'), 

																				)
			return  render(request,'registro_cliente.html',data)
		else:
			return  render(request,'registro_cliente.html',data)
	elif request.method == 'GET':
		ret_data['num_identidad'] = cliente.num_identidad
		ret_data['nombres'] = cliente.nombres
		ret_data['apellidos'] = cliente.apellidos
		ret_data['fecha_nacimiento'] = cliente.fecha_nacimiento
		ret_data['telefono'] = cliente.telefono
		ret_data['genero'] = cliente.genero.pk
		data = {'guardar_modificar':guardar_modificar,'id_cliente':id_cliente,'ret_data':ret_data,'generos':generos}
		return  render(request,'registro_cliente.html',data)

	
# def buscar_productos(request):
# 	if request.method == 'POST':
# 		lista = {}
# 		lista_buscar = vista de los productos.objects.filter(Q(nombre_producto__icontains=request.POST.get('Search')) 
# 													| Q(empresa__nombre__icontains=request.POST.get('Search'))
# 													| Q(descripcion_producto__icontains=request.POST.get('Search'))).filter(empresa__estado_aprobacion=3)
# 		print lista_buscar.query,"lista buscar"
# 		return render(request,'buscar_productos.html',{'empresas':lista_buscar})
# 	else:
# 		return render(request,'error.html')
def registrar_producto(request):
	generos = Genero.objects.all()
	categorias = Categoria.objects.all()
	productos = Producto.objects.all()
	if request.method == 'POST':
		ret_data,query_producto,errores = {},{},{}

		query_producto['nombre_producto'] = request.POST.get('nombre_producto')
		query_producto['imagen_producto'] = request.FILES.get('imagen_producto')
		query_producto['descripcion_producto'] = request.POST.get('descripcion_producto')
		query_producto['modelo'] = request.POST.get('modelo')
		query_producto['precio'] = request.POST.get('precio')
		query_producto['porcentaje_descuento'] = request.POST.get('porcentaje_descuento')
		query_producto['proveedor'] = request.POST.get('proveedor')
		query_producto['marca'] = Marca.objects.get(pk=int(request.POST.get('marca')))
		query_producto['categoria_genero'] = Genero.objects.get(pk=int(request.POST.get('categoria_genero')))

		if int(request.POST.get('esta_descuento')) == 2:
			query_producto['esta_descuento'] = True
		else:
			query_producto['esta_descuento'] = False


		if int(request.POST.get('nuevo_producto')) == 1:
			query_producto['nuevo_producto'] = True
		else:
			query_producto['nuevo_producto'] = False

		query_producto['estado_producto'] = True

		producto = Producto(**query_producto)
		producto.save()

		return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto'))
	else:
		data = {'generos':generos,'categorias':categorias,'productos':productos}
		return render(request,'registrar_producto.html',data)

def detalle_producto(request,id_producto):
	producto = Producto.objects.get(pk=id_producto);
	return render(request,'detalle_producto.html',{'producto':producto})

def lista_categorias(request):
	categorias = Categoria.objects.all();
	return render(request,'lista_categorias.html',{'categorias':categorias})

def ajax_categoria_marca(request):
	if request.method == "GET" and request.is_ajax():

		if request.GET.get('id_categoria') is not None:

			marcas_categorias = list(Marca.objects.filter(categoria=request.GET.get('id_categoria')).values('id','descripcion_marca'))
			if marcas_categorias:
				return JsonResponse(marcas_categorias,safe=False)
			else:
				return JsonResponse({'marcas_categorias':'nada'})



def agregar_empresa(request):
	guardar_editar = True
	ret_data,query_empresa,errores = {},{},{}

	if request.method == 'POST':
		ret_data['nombre'] = request.POST.get('nombre')
		ret_data['imagen_logo'] = request.FILES.get('imagen_logo')
		ret_data['contacto'] = request.POST.get('contacto')
		ret_data['correo'] = request.POST.get('correo')
		ret_data['direccion'] = request.POST.get('direccion')
		ret_data['latitude_empresa'] = request.POST.get('latitude_empresa')
		ret_data['longitude_empresa'] = request.POST.get('longitude_empresa')
		ret_data['descripcion'] = request.POST.get('descripcion')

		#1
		if request.POST.get('nombre') == '':
			errores['nombre'] = "Por favor ingrese el nombre de la Empresa"
		else:
			query_empresa['nombre'] = request.POST.get('nombre')

		#2
		if request.FILES.get('imagen_logo') == None:
			errores['imagen_logo'] = "Por favor ingrese el logo de la Empresa"
		else:
			query_empresa['imagen_logo'] = request.FILES.get('imagen_logo')

		#3
		if request.POST.get('contacto') == '':
			errores['contacto'] = "Por favor ingrese el contacto de la Empresa"
		else:
			query_empresa['contacto'] = request.POST.get('contacto')

		#4
		if request.POST.get('correo') == '':
			errores['correo'] = "Por favor ingrese el correo de la Empresa"
		else:
			query_empresa['correo'] = request.POST.get('correo')

		#5
		if request.POST.get('direccion') == '':
			errores['direccion'] = "Por favor ingrese la direccion de la Empresa"
		else:
			query_empresa['direccion'] = request.POST.get('direccion')

		#6
		if request.POST.get('latitude_empresa') == '':
			errores['latitude_empresa'] = "Por favor ingrese la latitude de la Empresa"
		else:
			query_empresa['latitude_empresa'] = request.POST.get('latitude_empresa')

		#7
		if request.POST.get('longitude_empresa') == '':
			errores['longitude_empresa'] = "Por favor ingrese la longitude de la Empresa"
		else:
			query_empresa['longitude_empresa'] = request.POST.get('longitude_empresa')

		#8
		if request.POST.get('descripcion') == '':
			errores['descripcion'] = "Por favor ingrese la descripcion de la Empresa"
		else:
			query_empresa['descripcion'] = request.POST.get('descripcion')

		if not errores:
			try:
				empresa = Empresa(**query_empresa)
				empresa.save()
			except Exception as e:
				transaction.rollback()

				errores['administrador'] = "CONTACTAR AL ADMINISTEADOR DEL SISTEMA"
				ctx = {'errores':errores,'ret_data':ret_data, 'guardar_editar':guardar_editar}
				
				return render(request,'registrar_empresa.html',ctx)

			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa'))

		else:
			return redirect('ecommerce_app:agregar_empresa')


	else:
		return render(request,'agregar_empresa.html')

##Categoria Producto
def agregar_categoria(request):
	categorias = Categoria.objects.all()
	ret_data,query_categoria,errores = {},{},{}

	if request.method == 'POST':
		ret_data['descripcion_categoria'] = request.POST.get('descripcion_categoria')
		
		if request.POST.get('descripcion_categoria') == '':
			errores['descripcion_categoria'] = "Debe ingresar la Categoría"
			
		else:
			query_categoria['descripcion_categoria'] = request.POST.get('descripcion_categoria')

		if not errores:
			try:
				categoria = Categoria(**query_categoria)
				categoria.save()
				pass
			except Exception as e:
				transaction.rollback()
				errores['administrador'] = e
				ctx = {'categorias':categorias,'errores':errores,'ret_data':ret_data}

				return render(request,'agregar_categoria.html',ctx)
			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria'))
		else:
			ctx = {'categorias':categorias,'errores':errores,'ret_data':ret_data}
			return render(request,'agregar_categoria.html',ctx)
	else:
		ctx = {'categorias':categorias}
		return render(request,'agregar_categoria.html',ctx)

def modificar_categoria(request,id_categoria):
	categoria = Categoria.objects.get(pk=id_categoria)
	errores = {}
	
	if request.method == 'POST':

		if request.POST.get('descripcion_categoria') == '':
			errores['descripcion_categoria'] = "Ingrese la Categoría"

		if not errores:	
			try:
				categoria = Categoria.objects.filter(pk=id_categoria).update(descripcion_categoria=request.POST.get('descripcion_categoria'))
			except Exception as e:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria'))
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria'))
		else: 
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria'))
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria'))

##Categoria Genero
def agregar_genero(request):
	categoria_genero = Genero.objects.all()
	ret_data,query_categoria,errores = {},{},{}

	if request.method == 'POST':
		ret_data['descripcion_genero'] = request.POST.get('descripcion_genero')
		
		if request.POST.get('descripcion_genero') == '':
			errores['descripcion_genero'] = "Debe ingresar la descripción de Categoría Género"
			
		else:
			query_categoria['descripcion_genero'] = request.POST.get('descripcion_genero')

		if not errores:
			try:
				categoria_genero = Genero(**query_categoria)
				categoria_genero.save()
				pass
			except Exception as e:
				transaction.rollback()
				errores['administrador'] = e
				ctx = {'categoria_genero':categoria_genero,'errores':errores,'ret_data':ret_data}

				return render(request,'agregar_categoria_genero.html',ctx)
			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria_genero'))
		else:
			ctx = {'categoria_genero':categoria_genero,'errores':errores,'ret_data':ret_data}
			return render(request,'agregar_categoria_genero.html',ctx)
	else:
		ctx = {'categoria_genero':categoria_genero}
		return render(request,'agregar_categoria_genero.html',ctx)

def modificar_genero(request,id_genero):
	categorias_genero = Genero.objects.get(pk=id_genero)
	errores = {}
	
	if request.method == 'POST':

		if request.POST.get('descripcion_genero') == '':
			errores['descripcion_genero'] = "Ingrese la Categoría Género"

		if not errores:	
			try:
				categoria = Genero.objects.filter(pk=id_genero).update(descripcion_genero=request.POST.get('descripcion_genero'))
			except Exception as e:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_genero'))
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_genero'))
		else: 
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_genero'))
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_genero'))

##Marca
def agregar_marca(request):
	marcas = Marca.objects.all()
	categorias = Categoria.objects.all()
	ret_data,query_marca,errores = {},{},{}

	if request.method == 'POST':

		ret_data['descripcion_marca'] = request.POST.get('descripcion_marca')
		ret_data['categoria'] = Categoria.objects.get(pk=int(request.POST.get('categoria')))
		

		if request.POST.get('descripcion_marca') == '':
			errores['descripcion_marca'] = "Debe ingresar la Marca"
		else:
			query_marca['descripcion_marca'] = request.POST.get('descripcion_marca')
		
		query_marca['categoria'] = Categoria.objects.get(pk=int(request.POST.get('categoria')))

		if not errores:
			try:
				marca = Marca(**query_marca)
				marca.save()
				pass
			except Exception as e:
				transaction.rollback()
				errores['administrador'] = e
				ctx = {'marcas':marcas,'categorias':categorias,'errores':errores,'ret_data':ret_data}

				return render(request,'agregar_marca.html',ctx)
			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca'))
		else:
			ctx = {'marcas':marcas,'categorias':categorias,'errores':errores,'ret_data':ret_data}
			return render(request,'agregar_marca.html',ctx)
	else:
		ctx = {'marcas':marcas,'categorias':categorias}
		return render(request,'agregar_marca.html',ctx)

def modificar_marca(request,id_marca):
	marca = Marca.objects.get(pk=id_marca)
	errores = {}
	
	if request.method == 'POST':

		if request.POST.get('descripcion_marca') == '' or int(request.POST.get('categoria')) == 0:
			errores['descripcion_marca'] = "Ingrese la Marca del Producto"

		if not errores:	
			try:
				marca = Marca.objects.filter(pk=id_marca).update(descripcion_marca=request.POST.get('descripcion_marca'),
																 categoria=request.POST.get('categoria'))
			except Exception as e:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca'))
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca'))
		else: 
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca'))
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca'))

