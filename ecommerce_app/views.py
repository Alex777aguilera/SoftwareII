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
	if request.user.is_authenticated:
		if request.user.is_superuser :
			return redirect('ecommerce_app:principal_admin')
		else:
			return render(request,'principal.html')
	else:
		return render(request,'principal.html')


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
	return render(request,'registrar_producto.html')

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

