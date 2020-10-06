from django.shortcuts import render,redirect
from django.db import transaction,connections
from django.contrib.auth import login as auth_login,logout,authenticate
from django.http import HttpResponseRedirect,JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import *
from django.conf import settings
from django.db.models import Sum
import json, re, telegram, os 
from datetime import datetime
from django.core.mail import EmailMessage

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
# def perfil_cliente(request):
# 	user = request.user
# 	if user.is_authenticated:
# 		if request.user.is_superuser :
# 			return redirect('ecommerce_app:principal_admin')
# 		else:
# 			return render(request,'perfil_cliente.html')	
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
	
# def buscar_productos(request):
# 	if request.method == 'POST':
# 		lista = {}
# 		lista_buscar = vista de los productos.objects.filter(Q(nombre_producto__icontains=request.POST.get('busqueda')) 
# 													| Q(empresa__nombre__icontains=request.POST.get('busqueda'))
# 													| Q(descripcion_producto__icontains=request.POST.get('busqueda'))).filter(empresa__estado_aprobacion=3)
# 		print lista_buscar.query,"lista buscar"
# 		return render(request,'buscar_productos.html',{'empresas':lista_buscar})
# 	else:
# 		return render(request,'error.html')

def registrar_producto(request):
	return render(request,'registrar_producto.html')

@login_required
def agregar_empresa(request):
	guardar_editar = True
	empresas = Empresa.objects.all()
	ret_data,query_empresa,errores = {},{},{}

	if request.method == 'POST':
		ret_data['nombre'] = request.POST.get('nombre')
		ret_data['imagen_logo'] = request.FILES.get('imagen_logo')
		ret_data['telefono'] = request.POST.get('telefono')
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
		if request.POST.get('telefono') == '':
			errores['telefono'] = "Por favor ingrese el contacto de la Empresa"
		else:
			query_empresa['telefono'] = request.POST.get('telefono')

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
				print (e)
				errores['administrador'] = "CONTACTAR AL ADMINISTEADOR DEL SISTEMA"
				ctx = {'errores':errores,'ret_data':ret_data, 'guardar_editar':guardar_editar,'empresas':empresas}
				
				return render(request,'agregar_empresa.html',ctx)

			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa'))

		else:
			ctx = {'errores':errores,'ret_data':ret_data, 'guardar_editar':guardar_editar,'empresas':empresas}
			return render(request,'agregar_empresa.html',ctx)

	else:
		ctx = {'empresas':empresas}
		return render(request,'agregar_empresa.html',ctx)

#vista carrito
def carrito(request):
	user = request.user
	print (user)
	if user.is_authenticated:
		if request.user.is_superuser :
			return redirect('ecommerce_app:principal')
		else:
			return render(request,'carrito.html')
	else:
		return render(request,'carrito.html')
