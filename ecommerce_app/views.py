from django.shortcuts import render,redirect #Rendirzado de plantillas y vista
from django.contrib.auth import login as auth_login,logout,authenticate #Atenticacion Django
from django.http import HttpResponseRedirect,JsonResponse, HttpResponse #Respuestas a nivel web
from django.urls import reverse #Manejo de vistas
from django.contrib.auth.models import * #Modelos de nuestra APP
from django.conf import settings #Configuracion de nuestro proyecto
from django.db.models import Sum,Q 
from django.db import transaction,connections #manejo de base de datos
import json, re, os #formato json, paquete y sistema
from datetime import datetime #Paquete de python para fechas
from django.core.mail import EmailMessage #Paquete de python para correo
from django.contrib.auth.hashers import make_password #Paquete de python para contreseña
from django.core import serializers #Serializadores para convertir objetos a json
from django.core.paginator import Paginator #Paginador para html
from django.contrib.auth.decorators import login_required, permission_required #Manejo de permisos
from django.template.loader import get_template #Manejo de plantillas HTMl

from ecommerce_app.models import * #Modelos de nuestra aplicacion
from decimal import Decimal #Paquete
from pprint import PrettyPrinter #Manejo de PDF

#Librerias para PDF
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import StringIO
from io import BytesIO

'''
Lo anterior son todas librerias de terceros, de python y django que son necesarias
para el funcionamiento de la aplicacion, tambien configuraciones y paquetes necesarios.
'''

'''
Por delante nos encontramos con la logica de nuestro proyecto, donde se rendereiza a plantillas
junto con sus datos respectivos, validaciones,atenticaciones, manejo de eventos asincronos, 
envios de correo, generacion de reportes etc.
'''
existe = '' #variable global
#vista principal por aqui se redirige al tipo de usuario
def principal(request):
	consulta = request.GET.get('busqueda') #Busqueda de productos
	if consulta:
		#filtros de la consulta
		productos = Producto.objects.filter(
			Q(nombre_producto__icontains=consulta)	|
			Q(descripcion_producto__icontains=consulta) |
			Q(marca__subcategoria__descripcion_subcategoria__icontains=consulta) |
			Q(marca__subcategoria__categoria__descripcion_categoria__icontains=consulta) |
			Q(marca__descripcion_marca__icontains=consulta),
			estado_producto = True 
		).distinct().order_by('id')
		categorias = Categoria.objects.all()
		subcategorias = SubCategoria.objects.all()
		paginator = Paginator(productos, 6)
		#paginador para los resultados
		page_number = request.GET.get('page')
		productos = paginator.get_page(page_number)
		data = {'productos':productos,'categorias':categorias,'subcategorias':subcategorias}
		return render(request, 'productos_busqueda.html', data)
	else:
		#Data para nuestro index
		productos_recientes = Producto.objects.filter(estado_producto=True).order_by('-id')[:8]
		productos_femeninos = Producto.objects.filter(categoria_genero=2).order_by('-id')[:8]
		productos_masculinos = Producto.objects.filter(categoria_genero=1).order_by('-id')[:8]

		categorias = Categoria.objects.get(pk=1)
		empresas = Empresa.objects.get(pk=1)
		a=1

		data = {'productos_recientes':productos_recientes,'productos_femeninos':productos_femeninos,
				'productos_masculinos':productos_masculinos,'categorias':categorias,'a':a,
				'empresas':empresas}
		if request.user.is_authenticated:
			if request.user.is_superuser :
				#Si es super usuario redirige a plantilla admin
				return redirect('ecommerce_app:principal_admin')
			else:
				#Si no a plantilla prinicpal
				return render(request,'principal.html',data)
		else:
			#Si no esta autenticado plantilla principal
			return render(request,'principal.html',data)


## Vista admin con su data
@login_required
def principal_admin(request):
	user = request.user
	if user.is_authenticated:
		if request.user.is_superuser :
			ordenes = Orden.objects.all()
			clientes = Cliente.objects.all()
			data= {'ordenes':ordenes,'clientes':clientes}
			return render(request,'inicio_admin.html',data)
		else:
			return redirect('ecommerce_app:principal')
			
		
	else:
		return render(request,'error.html')

#vista cliente
@login_required
def perfil_cliente(request):
	user = request.user
	empresas = Empresa.objects.get(pk=1)
	if user.is_authenticated:
		if request.user.is_superuser :
			return redirect('ecommerce_app:principal_admin')
		else:

			generos = Genero.objects.exclude(pk=3).exclude(pk=4)
			cliente = Cliente.objects.get(usuario_cliente = user)
			domicilio = Domicilio.objects.get(usuario = user)

			data = {'cliente':cliente,'domicilio':domicilio,'generos':generos,'empresas':empresas}
			return render(request,'perfil_cliente.html',data)	
	else:
		return render(request,'error.html')


#Vista para el login con sus validaciones
def login(request):
	if request.user.is_authenticated:
		if request.user.is_superuser :
			return redirect('ecommerce_app:principal_admin')
		else:
			return redirect('ecommerce_app:principal')	
	empresas = Empresa.objects.get(pk=1)
	mensaje = ''
	if request.method == 'POST':
		username = request.POST.get('username')
		contrasenia = request.POST.get('pass')
		user = authenticate(username=username,password=contrasenia)
		#Consulta si el usuario tiene una cuenta 
		if user is not None:
			
			if user.is_active:#Si el usuario esta activo
				auth_login(request,user)
				
				if request.user.is_superuser :#Validacion
					return redirect('ecommerce_app:principal_admin')
				else:
					return redirect('ecommerce_app:principal')	
	
			else:
				mensaje = 'USUARIO INACTIVO'
				ctx = {'mensaje':mensaje,'empresas':empresas}
				return render(request,'login.html',ctx)
		else:
			mensaje = 'USUARIO O CONTRASEÑA INCORRECTO'
			ctx = {'mensaje':mensaje,'empresas':empresas}
			return render(request,'login.html',ctx)

	ctx = {'empresas':empresas}
	return render(request,'login.html',ctx)


#vista para cerrar sesion
def cerrar_sesion(request):
	logout(request)
	return HttpResponseRedirect(reverse('ecommerce_app:login'))

#Para registrar cliente
def registro_cliente(request):
	if request.user.is_superuser or request.user.is_authenticated:
		return redirect('ecommerce_app:principal')	
	else:
		guardar_modificar = True
		empresas = Empresa.objects.get(pk=1)
		genero = Genero.objects.exclude(pk=3).exclude(pk=4)
		rango = 0
		username = ''
		lista_correo = []

		query_cliente,query_domicilio,ret_data,errores,errores_domicilio = {},{},{},{},{}
		if request.method == 'POST':#Si es metodo post guardara en la base de datos
			existe_usuario = False
			correo = request.POST.get('Correo')
			usuario = User.objects.filter(username=correo)

			ret_data['num_identidad'] = request.POST.get("identificacion")
			ret_data['nombres'] = request.POST.get("nombres")
			nombres  = request.POST.get('nombres')
			ret_data['apellidos'] = request.POST.get("apellidos")
			apellidos = request.POST.get('apellidos')
			
			ret_data['numero_telefono'] = request.POST.get("telefono")
			ret_data['fecha_nacimiento'] = request.POST.get("fecha_nacimiento")
			ret_data['correo'] = request.POST.get("Correo")
			ret_data['direccion'] = request.POST.get("direccion")
			ret_data['genero'] = int(request.POST.get("genero"))
			ret_data['imagen'] = request.FILES.get("imagen")
			email = request.POST.get('correo')
			ret_data['imagen'] = request.POST.get("imagen")
			
			if request.POST.get("identificacion") == '':
				errores['num_identidad'] = "DEBES INGRESAR LA IDENTIDAD"
			else:
				query_cliente["num_identidad"] = request.POST.get("identificacion")	
			
			if request.POST.get("nombres") == '':
				errores['nombres'] = "DEBES INGRESAR DATOS"
			else:
				query_cliente["nombres"] = request.POST.get("nombres")

			if request.POST.get("apellidos") == '':
				errores['apellidos'] = "DEBES INGRESAR EL APELLIDO"
			else:
				query_cliente["apellidos"] = request.POST.get("apellidos")
			
			if request.POST.get("fecha_nacimiento") == '':
				errores['fecha_nacimiento'] = "DEBES INGRESAR LA FECHA DE NACIMIENTO YY-MM-DD"
			else:
				query_cliente["fecha_nacimiento"] = request.POST.get("fecha_nacimiento")
			if request.POST.get("telefono") == '':
				errores['numero_telefono'] = "DEBES INGRESAR EL NUMERO"
			else:
				query_cliente["numero_telefono"] = request.POST.get("telefono")
			if request.POST.get("Correo") == '':
				errores['correo'] = "DEBES INGRESAR EL CORREO"
			else:
				query_cliente["correo"] = request.POST.get("Correo")
				
			if request.POST.get("genero") == '':
				errores['genero'] = "DEBES SELECIONAR UN GENERO"
			else:
				query_cliente["genero"] = Genero.objects.get(pk=int(request.POST.get("genero")))
			
			if request.FILES.get("imagen") == None:
				query_cliente["imagen"] =  'Media/imagen_cliente/cliente_default.jpg'
			else:
				query_cliente["imagen"] = request.FILES.get("imagen")


			password = BaseUserManager().make_random_password(7)
			lista_correo.append(correo)
			rango = correo.find('@') #Devulve la posicion donde esta el @
			for x in range(0,rango):
				username += correo[x]
				
			# Creacion del domicilio
			ret_data['direccion'] = request.POST.get("direccion")

			if request.POST.get("direccion") == '':
				errores_domicilio['direccion'] = "DEBES INGRESAR TU DOMICILIO"
			else:
				query_domicilio["direccion"] = request.POST.get("direccion")

			if Cliente.objects.filter(correo=query_cliente['correo']).exists(): 
				#Si el correo ya existe en la base de datos
				errores['existe'] = 'Por favor, ingrese otro correo'

				
			if not errores and not errores_domicilio:
				try:
					#Creación de usuario
					User.objects.create_user(username, email, password)
					user = User.objects.last()
					# guardado para Cliente
					query_cliente['usuario_cliente'] = user
					cliente = Cliente(**query_cliente)
					cliente.save()
					# guardado para Domicilio
					query_domicilio['usuario'] = user
					domicilo = Domicilio(**query_domicilio)
					domicilo.save()

					try:
						#Envío de correo a usuario
						email_data = {'nombres':nombres,'usuario':username,'contrasena':password}
						message = get_template('email.html').render(email_data, request=request)
						msg = EmailMessage('Creación de usuario', message, settings.EMAIL_HOST_USER, 
											lista_correo)
						msg.content_subtype = 'html'
						msg.send(fail_silently=False)
					except Exception as e:
						pass
					else:
						pass
				except Exception as e:
					transaction.rollback()
					
					data = {'generos':genero,'ret_data':ret_data,
						'errores':errores,'guardar_modificar':guardar_modificar,'errores_domicilio':errores_domicilio,'empresas':empresas}
					return render(request,'registro_cliente.html',data)

				else:
					transaction.commit()

					return HttpResponseRedirect(reverse('ecommerce_app:registro_cliente')+"?ok")
			else:
				data = {'generos':genero,'ret_data':ret_data,
						'errores':errores,'guardar_modificar':guardar_modificar,'errores_domicilio':errores_domicilio,'empresas':empresas}
				return render(request,'registro_cliente.html',data)

		elif request.method	== 'GET':	
			data = {'generos':genero,'guardar_modificar':guardar_modificar,'empresas':empresas}
			return render(request,'registro_cliente.html',data)

	# elif request.method	== 'GET':	
	# 	data = {'generos':genero,'guardar_modificar':guardar_modificar,'empresas':empresas}
	# 	return render(request,'registro_cliente.html',data)

#Vista para modificar cliente con sus parametros
@login_required	
def modificar_cliente(request,id_cliente):
	clien = Cliente.objects.get(pk=id_cliente)
	ret_data,query_cliente,errores = {},{},{}
	if request.method=='POST':
		if request.POST.get('nombres') == '' or request.POST.get('apellidos') == '' or request.POST.get('num_identidad') == '' or request.POST.get('numero_telefono') =='' or request.POST.get('fecha_nacimiento') =='' or request.POST.get('correo') =='' or int(request.POST.get('genero')) == 0:
			errores['nombres'] = "HAY ERRORES!"
		if not errores:
			try: 
				clien = Cliente.objects.filter(pk=id_cliente).update(
																			 num_identidad = request.POST.get('num_identidad'),
																			 nombres = request.POST.get('nombres'),
																			 apellidos = request.POST.get('apellidos'),	
																			 numero_telefono = request.POST.get('numero_telefono'),																			 
																			 fecha_nacimiento = request.POST.get('fecha_nacimiento'),	
																			 correo = request.POST.get('correo'),
																			 genero = request.POST.get('genero'),																			 
																			 ),
			except Exception as e:
				print (e)
				return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?error")
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?ok3")		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?error")
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente'))

@login_required
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
#Vista para modificar imagenes
@login_required
def modificar_img_cliente(request,id_cliente):
	avatar = Cliente.objects.get(pk=id_cliente)
	ret_data,query_cliente,errores = {},{},{}

	if request.method=='POST':
		if request.FILES.get('imagen') == None:
			errores['errores'] = "HAY ERRORES!"

		if not errores:
			try: 
				if avatar.imagen == 'Media/imagen_cliente/cliente_default.jpg':
					#Ubicacion de la ruta de nuestro servidor de archivos en Amazon S3
					#Si contiene imagen por defecto no elimina la imagen y la cambio
					avatar.imagen = request.FILES.get('imagen')
					avatar.save()
				else:
					#Caso contrario la elimina
					avatar.imagen.delete()
					avatar.imagen = request.FILES.get('imagen')
					avatar.save()  

			except Exception as e:	
				return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?error2")
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?ok2")		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?error2")
		
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente'))

@login_required
def modificar_domicilio(request,id_domicilio):
	domicilio = Domicilio.objects.get(pk=id_domicilio)
	ret_data,errores = {},{}
	if request.method=='POST':
		if request.POST.get('direccion') == '':
			errores['direccion'] = "HAY ERRORES!"
		if not errores:
			try: 
				domicilio = Domicilio.objects.filter(pk=id_domicilio).update(
																			 direccion = request.POST.get('direccion'),
																			 																			 
																			 ),
			except Exception as e:
				print (e)
				return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?errord")
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?okd")		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente')+"?errord")
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:perfil_cliente'))
def email(request):
	return render(request,'email.html')
	

#Vista necesaria para registrar un producto
@login_required
def registrar_producto(request):
	if request.user.is_superuser:
		generos = Genero.objects.all()
		categorias = Categoria.objects.all()
		productos = Producto.objects.all()
		subcategorias = SubCategoria.objects.all()
		marcas = Marca.objects.all()
		if request.method == 'POST':
			ret_data,query_producto,errores = {},{},{}

			ret_data['nombre_producto'] = request.POST.get('nombre_producto')
			ret_data['precio'] = request.POST.get('precio')

			query_producto['imagen_producto'] = request.FILES.get('imagen_producto')
			query_producto['descripcion_producto'] = request.POST.get('descripcion_producto')
			query_producto['modelo'] = request.POST.get('modelo')
			query_producto['porcentaje_descuento'] = request.POST.get('porcentaje_descuento')
			query_producto['proveedor'] = request.POST.get('proveedor')

			if int(request.POST.get('esta_descuento')) == 2: #Por defecto es 1 que es false no esta en descuento
				query_producto['esta_descuento'] = True
			
			if int(request.POST.get('nuevo_producto')) == 2: #Por defecto es 1 que es True es un producto nuevo
				query_producto['nuevo_producto'] = False
			#1
			if request.POST.get('nombre_producto') == '':
				errores['nombre_producto'] = "Por favor ingrese el nombre del Producto"
			else:
				query_producto['nombre_producto'] = request.POST.get('nombre_producto')
			#2	
			if request.POST.get('precio') == '':
				errores['precio'] = "Por favor ingrese el precio del Producto"
			else:
				query_producto['precio'] = request.POST.get('precio')
			#3
			if request.POST.get('porcentaje_descuento') == '':
				errores['porcentaje_descuento'] = 0
			#4	
			if request.FILES.get('imagen_producto') == None:
				query_producto['imagen_producto'] = 'logo_proyecto.jpg'
			else:
				query_producto['imagen_producto'] = request.FILES.get('imagen_producto')
			#5
			if int(request.POST.get('marca')) == 0:
				errores['marca'] = "Por favor debe seleccionar la marca"
			else:
				query_producto['marca'] = Marca.objects.get(pk=int(request.POST.get('marca')))
			#6
			if int(request.POST.get('categoria_genero')) == 0:
				errores['categoria_genero'] = "Por favor debe seleccionar el genero"
			else:
				query_producto['categoria_genero'] = Genero.objects.get(pk=int(request.POST.get('categoria_genero')))
		
			if not errores:
				try:
					producto = Producto(**query_producto)
					producto.save()
				except Exception as e:
					transaction.rollback()
					errores['administrador'] = "CONTACTAR AL ADMINISTEADOR DEL SISTEMA"
					ctx = {'generos':generos,'categorias':categorias,'marcas':marcas,
					'subcategorias':subcategorias,'productos':productos,
					'errores':errores,'ret_data':ret_data}
					return render(request,'registrar_producto.html',ctx)
				else:
					transaction.commit()
					return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto')+"?ok")
			else:
				ctx = {'generos':generos,'categorias':categorias,'marcas':marcas,
				'subcategorias':subcategorias,'productos':productos,
				'errores':errores,'ret_data':ret_data}
				return render(request,'registrar_producto.html',ctx)
		else:
			data = {'generos':generos,'categorias':categorias,'marcas':marcas,
					'subcategorias':subcategorias,'productos':productos}
			return render(request,'registrar_producto.html',data)
	else:
		return redirect('ecommerce_app:principal')	

## Modificar producto
@login_required
def modificar_producto(request,id_producto):
	productos = Producto.objects.get(pk=id_producto)
	ret_data,query_producto,errores = {},{},{}
	bool_descuento = False
	bool_nuevo_producto = True
	bool_estado_producto= True

	if request.method=='POST':
		if request.POST.get('nombre_producto') == '' or request.POST.get('precio') == '':
			errores['errores'] = "HAY ERRORES!"

		if not errores:
			if int(request.POST.get('esta_descuento')) == 2:
				bool_descuento = True
			if int(request.POST.get('nuevo_producto')) == 2: #Por defecto es 1 que es True es un producto nuevo
				bool_nuevo_producto = False
			if int(request.POST.get('estado_producto')) == 2: #Por defecto es 1 que es True es un producto activo
				bool_estado_producto = False

			try: 
				productos =Producto.objects.filter(pk=id_producto).update(
																	nombre_producto = request.POST.get('nombre_producto'),
																	descripcion_producto = request.POST.get('descripcion_producto'),
																	modelo = request.POST.get('modelo'),
																	precio = request.POST.get('precio'),
																	porcentaje_descuento = request.POST.get('porcentaje_descuento'),
																	proveedor = request.POST.get('proveedor'),
																	esta_descuento = bool_descuento,
																	nuevo_producto = bool_nuevo_producto,
																	estado_producto = bool_estado_producto,
																	marca = Marca.objects.get(pk=int(request.POST.get('marca'))),
																	categoria_genero = Genero.objects.get(pk=int(request.POST.get('categoria_genero'))),
																),

			except Exception as e:
				return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto')+"?error1")
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto')+"?ok1")		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto')+"?error1")
		
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto'))

#Modificar imagen de producto
@login_required			
def modificar_img_producto(request,id_producto):
	producto = Producto.objects.get(pk=id_producto)
	ret_data,query_producto,errores = {},{},{}

	if request.method=='POST':
		if request.FILES.get('imagen_producto') == None:
			errores['errores'] = "HAY ERRORES!"

		if not errores:
			try: 
				if producto.imagen_producto == 'Media/productos_empresa/producto_default.png':
					producto.imagen_producto = request.FILES.get('imagen_producto')
					producto.save()
				else:
					producto.imagen_producto.delete()
					producto.imagen_producto = request.FILES.get('imagen_producto')
					producto.save() 

			except Exception as e:
				return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto')+"?error2")
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto')+"?ok2")		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto')+"?error2")
		
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:registrar_producto'))
#Vista necesario para el html de detalle de producto
def detalle_producto(request,id_producto):
	if request.user.is_superuser :
		return redirect('ecommerce_app:principal_admin')	
	else:
		empresas = Empresa.objects.get(pk=1)
		productos = Producto.objects.get(pk=id_producto)

		if Lote.objects.filter(producto=id_producto).exists() :
			existencias = Lote.objects.get(producto=id_producto)
		else:
			existencias = 0	
		rx = 1
		ctx = {'productos':productos,'existencias':existencias,'empresas':empresas,'rx':rx}
		return render(request,'detalle_producto.html',ctx)
#peticion ajax asincrona para consultar la existencia de ese producto
def ajax_existencia(request):
	existencia_p = 0
	if request.method == "POST" and request.is_ajax():
		if request.POST.get('id_producto') is not None:
			try:
				existencia_p = Lote.objects.get(producto=request.POST.get('id_producto'))
			except Exception as e:
				otra_variable = '0'
			else:
				otra_variable = serializers.serialize('json', [ existencia_p ])
				
			if existencia_p:
				return JsonResponse(otra_variable,safe=False)
			else:
				return JsonResponse({'otra_variable':'nada'})
	else :
		return JsonResponse({'otra_variable':'0'})




#vista carrito
@login_required
def carrito(request):
	empresas = Empresa.objects.get(pk=1)
	rx = 0
	user = request.user
	if user.is_authenticated:
		if request.user.is_superuser :
			return redirect('ecommerce_app:principal')
		else:
			
			carritos = Carrito.objects.filter(usuario=request.user)
							
			existencias = Lote.objects.all()
			cant_pro = Carrito.objects.filter(usuario=request.user).aggregate(cant_total=Sum('cantidad'))
			d = 0
			e = 0 #subtotal
			f = 0
			g = 0 #descuento
			ac = 0
			total = 0
			carrito_vacio = 1
			if cant_pro['cant_total'] == None:
				carrito_vacio = 0
				ctx = {'carrito_vacio':carrito_vacio}
				render(request,'carrito.html',ctx)
			
			# print(carritos.cantidad)
			for carrito in carritos:
				
				d = float(carrito.cantidad) * carrito.producto.precio #sacamos el subtotal de cantidad producto por el precio del mismo
				f = (int(carrito.producto.porcentaje_descuento)/100) #convertimos un entero en decimal, para poder sacar el % de descuento
				ac = (d*f)
				e += d #subtotal
				g += ac #descuento
			
			total = (e - g)

			if request.method == 'POST':
				a = request.POST.get('producto_id')
				b = int(request.POST.get('cantidad_d'))
				c = 0
				dx = 0

				ret_data,query_add_carrito,errores = {},{},{}
				if Carrito.objects.filter(producto=a,usuario=request.user).exists():
					## Validacion para sumar productos ya agregados al carrito
					carritos = Carrito.objects.filter(usuario=request.user)
					cant_p = Carrito.objects.filter(producto=a).aggregate(pro_total=Sum('cantidad'))
					c = int(cant_p['pro_total']) + b #cantidad de productos agregados
					
					carro = Carrito.objects.filter(producto=a).update(cantidad=c)

					###### Validacion para reducir los productos agregados al carrito en existencia
					cant_p_existencia = Lote.objects.get(producto=a)
					dx = (int(cant_p_existencia.existencia) - b)
					print(cant_p_existencia,"\n",dx)
					productos_apartados = Lote.objects.filter(producto=a).update(existencia=dx)


					errores["existe"] = "Se agrego con exito"
					ctx = {'carrito_vacio':carrito_vacio,'total':total,'g':g,'e':e,'errores':errores,'ret_data':ret_data,'carritos':carritos,'existencias':existencias,'empresas':empresas,'rx':rx}
					return HttpResponseRedirect(reverse('ecommerce_app:carrito'))

				
				ret_data['cantidad'] = request.POST.get('cantidad_d')

				if request.POST.get('cantidad_d') == '':
					errores['cantidad'] = "Debe ingresar la cantidad de productos a comprar"
				else:
					query_add_carrito['cantidad'] = request.POST.get('cantidad_d')
				
				if request.POST.get('producto') == '':
					errores['producto'] = "Debe ingresar la cantidad de productos a comprar"
				else:
					query_add_carrito['producto'] = Producto.objects.get(pk=int(request.POST.get('producto_id')))
					
				query_add_carrito['usuario'] = request.user

				if not errores:
					try:
						
						###### Validacion para reducir los productos agregados al carrito en existencia
						cant_p_existencia = Lote.objects.get(producto=a)
						dx = (int(cant_p_existencia.existencia) - b)
						print(cant_p_existencia,"\n",dx)
						productos_apartados = Lote.objects.filter(producto=a).update(existencia=dx)
						car = Carrito(**query_add_carrito)
						car.save()
						print("se guardo")
						
					except Exception as e:
						transaction.rollback()
						print (e)
						rx = 0
						existencias = Lote.objects.get(producto=a)
						errores['administrador'] = "CONTACTAR AL ADMINISTEADOR DEL SISTEMA"
						ctx = {'carrito_vacio':carrito_vacio,'total':total,'g':g,'e':e,'errores':errores,'ret_data':ret_data,'carritos':carritos,'existencias':existencias,'empresas':empresas,'rx':rx}
						
						return render(request,'carrito.html',ctx)

					else:
						transaction.commit()
						return HttpResponseRedirect(reverse('ecommerce_app:carrito'))

				else:
					rx = 0
					productos = Producto.objects.get(pk=a)
					existencias = Lote.objects.get(producto=a)
					print(productos)
					ctx = {'carrito_vacio':carrito_vacio,'total':total,'g':g,'e':e,'errores':errores,'ret_data':ret_data,'productos':productos,'existencias':existencias,'empresas':empresas,'rx':rx}
					return render(request,'detalle_producto.html',ctx)
			ctx = {'carrito_vacio':carrito_vacio,'total':total,'g':g,'e':e,'carritos':carritos,'existencias':existencias,'empresas':empresas,'rx':rx}
			return render(request,'carrito.html',ctx)
	else:
		return render(request,'carrito.html')

@login_required
##Eliminar producto carrito
def Eliminar_producto_carrito(request,id_Pdelete):
	#### Validacion, la cantidad de productos a existencia, en caso no realizen la compra
	car = Carrito.objects.get(pk=id_Pdelete)
	cant_p_existencia = Lote.objects.get(producto=car.producto)
	cant_pro = (int(car.cantidad) + int(cant_p_existencia.existencia))
	print(cant_pro)
	suma_car = Lote.objects.filter(producto=car.producto).update(existencia=cant_pro)
	#####
	eliminar = Carrito.objects.get(pk=id_Pdelete).delete()
	return HttpResponseRedirect(reverse('ecommerce_app:carrito'))



#Vista necesaria para cargar los combobox de manera asincrona a travesde AJAX
def ajax_categoria_subcategoria(request):
	if request.method == "GET" and request.is_ajax():

		if request.GET.get('id_categoria') is not None:
			subcategorias_categorias = list(SubCategoria.objects.filter(categoria=request.GET.get('id_categoria')).values('id','descripcion_subcategoria'))
			if subcategorias_categorias:
				return JsonResponse(subcategorias_categorias,safe=False)
			else:
				return JsonResponse({'subcategorias_categorias':'nada'})

#Vista necesaria para cargar los combobox de manera asincrona a travesde AJAX
def ajax_subcategoria_marca(request):
	if request.method == "GET" and request.is_ajax():
		if request.GET.get('id_subcategoria') is not None:
			marcas_subcategorias = list(Marca.objects.filter(subcategoria=request.GET.get('id_subcategoria')).values('id','descripcion_marca'))
			if marcas_subcategorias:
				return JsonResponse(marcas_subcategorias,safe=False)
			else:
				return JsonResponse({'marcas_subcategorias':'nada'})

#Vista para agregar una empresa
@login_required
def agregar_empresa(request):
	guardar_editar = True 
	empresas = Empresa.objects.all() 
	ret_data,query_empresa,errores = {},{},{}

	if request.method == 'POST':
		ret_data['nombre'] = request.POST.get('nombre') #Capturamos los valores que son ingresados en los textfield
		ret_data['imagen_logo'] = request.FILES.get('imagen_logo')
		ret_data['telefono'] = request.POST.get('telefono')
		ret_data['correo'] = request.POST.get('correo')
		ret_data['direccion'] = request.POST.get('direccion')
		ret_data['latitude_empresa'] = request.POST.get('latitude_empresa')
		ret_data['longitude_empresa'] = request.POST.get('longitude_empresa')
		ret_data['descripcion'] = request.POST.get('descripcion')

		#1  Validaciones para que los campos no vayan con valor nulo
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
				ctx = {'errores':errores,'ret_data':ret_data, 'guardar_editar':guardar_editar,'empresas':empresas} #Se envia el contexto a una variable
				
				return render(request,'agregar_empresa.html',ctx)  #rediereccionamiento de urls

			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa'))

		else:
			ctx = {'errores':errores,'ret_data':ret_data, 'guardar_editar':guardar_editar,'empresas':empresas}
			return render(request,'agregar_empresa.html',ctx)

	else:
		ctx = {'empresas':empresas}
		return render(request,'agregar_empresa.html',ctx)

##Categoria Producto
@login_required
def agregar_categoria(request):
	if request.user.is_superuser:
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
					return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria')+'?ok')
			else:
				ctx = {'categorias':categorias,'errores':errores,'ret_data':ret_data}
				return render(request,'agregar_categoria.html',ctx)
		else:
			ctx = {'categorias':categorias}
			return render(request,'agregar_categoria.html',ctx)
	else:
		return redirect('ecommerce_app:principal')	

@login_required
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
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria')+'?error1')
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria')+'?ok1')
		else: 
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria')+'?error1')
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_categoria'))

##Categoria Genero
@login_required
def agregar_genero(request):
	if request.user.is_superuser:
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
					return HttpResponseRedirect(reverse('ecommerce_app:agregar_genero'))
			else:
				ctx = {'categoria_genero':categoria_genero,'errores':errores,'ret_data':ret_data}
				return render(request,'agregar_categoria_genero.html',ctx)
		else:
			ctx = {'categoria_genero':categoria_genero}
			return render(request,'agregar_categoria_genero.html',ctx)
	else:
		return redirect('ecommerce_app:principal')	

@login_required
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

##Vista para agregar subcategoria
@login_required
def agregar_subcategoria(request):
	if request.user.is_superuser:
		categorias = Categoria.objects.all()
		subcategorias = SubCategoria.objects.all()
		ret_data,query_subcategoria,errores = {},{},{}

		if request.method == 'POST':
			ret_data['descripcion_subcategoria'] = request.POST.get('descripcion_subcategoria')
			ret_data['categoria'] = Categoria.objects.get(pk=int(request.POST.get('categoria')))

			if request.POST.get('descripcion_subcategoria') == '':
				errores['descripcion_subcategoria'] = "Debe ingresar la descripcion de la subcategoria"
			else:
				query_subcategoria['descripcion_subcategoria'] = request.POST.get('descripcion_subcategoria')
			
			if request.POST.get('categoria') == '':
				errores['categoria'] = "Debe seleccionar la Categoria"
			else:
				query_subcategoria['categoria'] = Categoria.objects.get(pk=int(request.POST.get('categoria')))

			if not errores:
				try:
					subcategoria = SubCategoria(**query_subcategoria)
					subcategoria.save()
					pass
				except Exception as e:
					transaction.rollback()
					errores['administrador'] = e
					ctx = {'categorias':categorias,'subcategorias':subcategorias,
							'errores':errores,'ret_data':ret_data}
					return render(request,'agregar_subcategoria.html',ctx)
				else:
					transaction.commit()
					return HttpResponseRedirect(reverse('ecommerce_app:agregar_subcategoria')+"?ok")
			else:
				ctx = {'categorias':categorias,'subcategorias':subcategorias,
						'errores':errores,'ret_data':ret_data}
				return render(request,'agregar_subcategoria.html',ctx)
		else:
			ctx = {'categorias':categorias,'subcategorias':subcategorias}
			return render(request,'agregar_subcategoria.html',ctx)
	else:
		return redirect('ecommerce_app:principal')	

@login_required
def modificar_subcategoria(request,id_subcategoria):
	subcategoria = SubCategoria.objects.get(pk=id_subcategoria)
	errores = {}
	
	if request.method == 'POST':

		if request.POST.get('descripcion_subcategoria') == '' or int(request.POST.get('categoria')) == 0:
			errores['error'] = "No debe dejar campos va"

		if not errores:	
			try:
				subcategoria = SubCategoria.objects.filter(pk=id_subcategoria).update(
															descripcion_subcategoria=request.POST.get('descripcion_subcategoria'),
														 	categoria=request.POST.get('categoria'))
			except Exception as e:
				transaction.rollback()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_subcategoria')+'?error1')
			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_subcategoria')+'?ok1')
		else: 
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_subcategoria')+'?error1')
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_subcategoria'))
##Vista para agregar marca
@login_required
def agregar_marca(request):
	if request.user.is_superuser:
		marcas = Marca.objects.all()
		sub_categorias = SubCategoria.objects.all()
		ret_data,query_marca,errores = {},{},{}

		if request.method == 'POST':
			print(request.POST.get('subcategoria'),"Esto trae")
			ret_data['descripcion_marca'] = request.POST.get('descripcion_marca')
			# ret_data['subcategoria'] = SubCategoria.objects.get(pk=int(request.POST.get('subcategoria')))
			

			if request.POST.get('descripcion_marca') == '':
				errores['descripcion_marca'] = "Debe ingresar la Marca"
			else:
				query_marca['descripcion_marca'] = request.POST.get('descripcion_marca')
			
			if request.POST.get('subcategoria') == '':
				errores['subcategoria'] = "Debe ingresar una sub categoria"
			else:
				query_marca['subcategoria'] = SubCategoria.objects.get(pk=int(request.POST.get('subcategoria')))

			if not errores:
				try:
					marca = Marca(**query_marca)
					marca.save()
					pass
				except Exception as e:
					transaction.rollback()
					errores['administrador'] = e
					ctx = {'marcas':marcas,'sub_categorias':sub_categorias,'errores':errores,'ret_data':ret_data}

					return render(request,'agregar_marca.html',ctx)
				else:
					transaction.commit()
					return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca')+"?ok")
			else:
				ctx = {'marcas':marcas,'sub_categorias':sub_categorias,'errores':errores,'ret_data':ret_data}
				return render(request,'agregar_marca.html',ctx)
		else:
			ctx = {'marcas':marcas,'sub_categorias':sub_categorias}
			return render(request,'agregar_marca.html',ctx)
	else:
		return redirect('ecommerce_app:principal')	

@login_required
def modificar_marca(request,id_marca):
	marca = Marca.objects.get(pk=id_marca)
	errores = {}
	
	if request.method == 'POST':

		if request.POST.get('descripcion_marca') == '' or int(request.POST.get('subcategoria')) == 0:
			errores['descripcion_marca'] = "Ingrese la Marca del Producto"

		if not errores:	
			try:
				marca = Marca.objects.filter(pk=id_marca).update(descripcion_marca=request.POST.get('descripcion_marca'),
																 subcategoria=request.POST.get('subcategoria'))
			except Exception as e:
				transaction.rollback()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca')+'?error1')
			else:
				transaction.commit()
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca')+'?ok1')
		else: 
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca')+'?error1')
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_marca'))

#Vista para agrear un lote 
@login_required
def registrar_lote(request):
	if request.user.is_superuser:
		productos = Producto.objects.all()
		lotes = Lote.objects.all()
		
		ret_data,query_lote,errores = {},{},{}
		if request.method == 'POST':
			ret_data['existencia'] = request.POST.get('existencia')
			print(request.POST.get('existencia'),"Esto contiene")
			if request.POST.get('existencia') == '':
				errores['existencia'] = "DEBE IGRESAR LA EXISTENCIA DEL PRODUCTO!!"
				
			else:
				query_lote['existencia'] = request.POST.get('existencia')

			if request.POST.get('producto') == '':
				errores['producto'] = "DEBE SELECIONAR EL PRODUCTO"
			else:
				query_lote['producto'] = Producto.objects.get(pk=int(request.POST.get('producto')))

			if not errores:
				try:
					existencia = Lote(**query_lote)
					existencia.save()
					
				except Exception as e:
					transaction.rollback()
					errores['administrador'] = e
					ctx = {'errores':errores,'ret_data':ret_data,'productos':productos,'lotes':lotes}

					return render(request,'registrar_lote.html',ctx)
				else:
					transaction.commit()
					return HttpResponseRedirect(reverse('ecommerce_app:registrar_lote')+'?ok')
			else:
				ctx = {'errores':errores,'ret_data':ret_data,'productos':productos,'lotes':lotes}
				return render(request,'registrar_lote.html',ctx)

		else:
			ctx = {'errores':errores,'ret_data':ret_data,'productos':productos,'lotes':lotes}
			return render(request,'registrar_lote.html',ctx)
	else:
		return redirect('ecommerce_app:principal')	

@login_required
def modificar_lote(request,id_lote):
	lotes = Lote.objects.get(pk=id_lote)
	errores = {}
	
	if request.method == 'POST':
		if request.POST.get('existencia') == '':
			errores['existencia'] = "Ingrese la Existencia "
		if not errores:	
			try:
				lote = Lote.objects.filter(pk=id_lote).update(existencia=request.POST.get('existencia'))
			except Exception as e:
				return HttpResponseRedirect(reverse('ecommerce_app:registrar_lote')+'?error1')
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:registrar_lote')+'?ok1')
		else: 
			return HttpResponseRedirect(reverse('ecommerce_app:registrar_lote')+'?error1')
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:registrar_lote'))

#Vista para renderizar a plantilla busqueda con sus filtros
def productos_categorias(request,id_categoria):
	productos = Producto.objects.filter(marca__subcategoria__categoria = id_categoria,
										estado_producto = True)
	categoria = Categoria.objects.get(pk=id_categoria)
	categorias = Categoria.objects.all()
	subcategorias = SubCategoria.objects.all()
	paginator = Paginator(productos, 6)

	page_number = request.GET.get('page')
	productos = paginator.get_page(page_number)
	data = {'productos':productos,'categorias':categorias,'categoria':categoria,
			'subcategorias':subcategorias}
	return render(request, 'productos_busqueda.html', data)

#Vista para renderizar a plantilla busqueda con sus filtros
def productos_subcategoria(request,id_categoria,id_subcategoria):
	productos = Producto.objects.filter(marca__subcategoria=id_subcategoria,
										estado_producto = True)
	categoria = Categoria.objects.get(pk=id_categoria)
	subcategoria = SubCategoria.objects.get(pk=id_subcategoria)
	categorias = Categoria.objects.all()
	subcategorias = SubCategoria.objects.all()
	paginator = Paginator(productos, 6)

	page_number = request.GET.get('page')
	productos = paginator.get_page(page_number)
	data = {'productos':productos,'categorias':categorias,'categoria':categoria,
			'subcategoria':subcategoria,'subcategorias':subcategorias}
	return render(request, 'productos_busqueda.html', data)

#Datos de los clientes en la plantilla de administrador
@login_required
def datos_clientes_admin(request):
	user = request.user
	if request.user.is_superuser :
		empresas = Empresa.objects.get(pk=1)
		clientes = Cliente.objects.all()
		domicilios = Domicilio.objects.all()
		data = {'empresas':empresas,'clientes':clientes,'domicilios':domicilios}
		return render(request,'datos_clientes_admin.html',data)
	else:
		return redirect('ecommerce_app:principal')	


@login_required
def Detalle_Orden(request):
	carritos = Carrito.objects.filter(usuario=request.user)
	a=0
	b=0
	c=0
	d=0
	e=0

	for carrito in carritos:
				
		a = float(carrito.cantidad) * carrito.producto.precio #sacamos el subtotal de cantidad producto por el precio del mismo
		b = (int(carrito.producto.porcentaje_descuento)/100) 
		c = (a*b)
		d += a 
		e += c
	
	total = (d - e)
	cliente = Cliente.objects.get(usuario_cliente=request.user)
	domicilio = Domicilio.objects.get(usuario = request.user)
	empresas = Empresa.objects.get(pk=1)
	ctx = {'carritos':carritos,'empresas':empresas,'cliente':cliente,'domicilio':domicilio,'d':d,'e':e,'total':total}
	### Validacion para eliminar los productos del carrito al ajercer la compra
	if request.method == 'POST' and request.POST.get('validacion'):
		c = int(request.POST.get('validacion'))
		if c == 1:
			# 
			return HttpResponseRedirect(reverse('ecommerce_app:Detalle_Orden')+"?dato")
		else :
			pass
	
	return render(request,'Detalle_Orden.html',ctx)

@login_required
def facturacion_producto(request):

	cliente = Cliente.objects.filter(usuario_cliente=request.user)
	cliente_correo = Cliente.objects.get(usuario_cliente=request.user)
	productos_carrito = Carrito.objects.filter(usuario=request.user)
	empresa = Empresa.objects.filter(pk=1)
	logo_emp = Empresa.objects.get(pk=1)

	query_orden = {}
	lista = []

	query_orden['metodo_pago'] = MetodoPago.objects.get(pk=1)
	query_orden['domicilio'] = Domicilio.objects.get(usuario=request.user)
	query_orden['usuario'] = request.user
	query_orden['subtotal'] = 0
	query_orden['descuento'] = 0
	query_orden['impuesto'] = 0
	query_orden['total'] = 0

	orden = Orden(**query_orden)
	orden.save()

	dic_data = {}
	subtotal_factura, desc_factura, sub_x_producto = 0, 0, 0

	for prod in productos_carrito:
		lista_data_prod = []

		sub_x_producto = prod.cantidad * Decimal(prod.producto.precio)

		if prod.producto.porcentaje_descuento == 0 or prod.producto.porcentaje_descuento == None:
			desc_prod = 0
		else:
			desc_prod = prod.producto.porcentaje_descuento

		desc_factura += desc_prod

		total_x_prod = sub_x_producto - desc_prod

		subtotal_factura += total_x_prod

		lista_data_prod.append(prod.cantidad)
		lista_data_prod.append(prod.producto.nombre_producto)
		lista_data_prod.append(f'Lps {prod.producto.precio}')
		lista_data_prod.append(f'Lps {desc_prod}')
		lista_data_prod.append(f'Lps {total_x_prod}')

		lista.append(lista_data_prod)

		detalle = DetalleOrden(cantidad=prod.cantidad,
								precio=prod.producto.precio,
								producto=Producto.objects.get(pk=prod.producto.pk),
								orden=Orden.objects.get(pk=orden.pk),
								descuento=desc_prod,
								total_producto=total_x_prod)
		detalle.save()

	isv = round((subtotal_factura * Decimal(0.15)),2)
	total_factura = round(((subtotal_factura + isv) - desc_factura),2)

	dic_data['detalle'] = lista

	orden.subtotal = subtotal_factura
	orden.impuesto = isv
	orden.descuento = desc_factura
	orden.total = total_factura
	orden.save()

	orden_factura = Orden.objects.filter(pk=orden.pk)

	ctx = {
	'factura' : dic_data,
	'subtotal' : subtotal_factura,
	'descuento' : desc_factura,
	'isv' : isv,
	'total' : total_factura,
	'cliente' : cliente,
	'orden_factura' : orden_factura,
	'empresa' : empresa,
	'logo_emp' : logo_emp.imagen_logo
	}

	template = get_template('factura_cliente.html')
	html = template.render(ctx)
	response = HttpResponse(content_type='application/pdf')  
	pisaStatus = pisa.CreatePDF(html,dest=response)
	car = Carrito.objects.filter(usuario = request.user).delete()

	#Enviamos un correo cuando generamos la factura
	correo = cliente_correo.correo
	lista_correo = []
	lista_correo.append(correo)

	try:
		message = get_template('factura_cliente.html').render(ctx, request=request)
		msg = EmailMessage('Factura', message, settings.EMAIL_HOST_USER,lista_correo)
		msg.content_subtype = 'html'
		msg.send(fail_silently=False)
	except Exception as e:
		pass
	else:
		pass

	return response

	# return render(request,'factura_cliente.html',ctx)
	

	
	

#vista para que el admin vea el pdf de todos los productos vendidos seleccionando un mes en especifico
@login_required
def pdf_mes_productos_vendidos(request):
	if request.method == 'POST':
		fecha = request.POST.get('mes')
		date = fecha.split('-')
		empresa = Empresa.objects.get(pk=1)
		lista = []
		dic_productos, dic, dic_total = {}, {}, {}
		no_ventas = False
		#fecha_reporte = datetime.now()

		if date[1] == '01':
			mes = 'Enero'

		elif date[1] == '02':
			mes = 'Febrero'

		elif date[1] == '03':
			mes = 'Marzo'

		elif date[1] == '04':
			mes = 'Abril'

		elif date[1] == '05':
			mes = 'Mayo'

		elif date[1] == '06':
			mes = 'Junio'

		elif date[1] == '07':
			mes = 'Julio'

		elif date[1] == '08':
			mes = 'Agosto'

		elif date[1] == '09':
			mes = 'Septiembre'

		elif date[1] == '10':
			mes = 'Octubre'

		elif date[1] == '11':
			mes = 'Noviembre'

		elif date[1] == '12':
			mes = 'Diciembre'

		#obteniendo el total de los productos vendidos filtrado por el mes
		facturas = Orden.objects.filter(fecha_compra__year=date[0], fecha_compra__month=date[1]).order_by('fecha_compra')
		total_cantidad = DetalleOrden.objects.filter(orden__fecha_compra__year=date[0], 
													orden__fecha_compra__month=date[1]
													).aggregate(total = Sum('cantidad'))['total']

		total_descuento = DetalleOrden.objects.filter(orden__fecha_compra__year=date[0], 
													orden__fecha_compra__month=date[1]
													).aggregate(total = Sum('descuento'))['total']

		total_precio = DetalleOrden.objects.filter(orden__fecha_compra__year=date[0], 
													orden__fecha_compra__month=date[1]
													).aggregate(total = Sum('precio'))['total']

		total_prod = DetalleOrden.objects.filter(orden__fecha_compra__year=date[0], 
													orden__fecha_compra__month=date[1]
													).aggregate(total = Sum('total_producto'))['total']


		if facturas.count() > 0:#validar que hay facturas realizadas en ese mes

			for factura in facturas:
				#obteniendo cada uno de los productos vendidos de esa factura en el mes
				productos_vendidos = DetalleOrden.objects.filter(orden=factura.pk)

				for producto in productos_vendidos:
					lista_producto = []

					lista_producto.append(producto.orden.fecha_compra.strftime("%d/%m/%Y"))
					lista_producto.append(producto.orden.pk)
					lista_producto.append(producto.producto.nombre_producto)
					lista_producto.append(producto.cantidad)
					lista_producto.append(f'Lps {producto.precio}')
					lista_producto.append(f'Lps {producto.descuento}')
					lista_producto.append(f'Lps {producto.total_producto}')

					lista.append(lista_producto)

			dic_total['total'] = [total_cantidad, f'Lps {total_precio}', f'Lps {total_descuento}', f'Lps {total_prod}']

			dic_productos['productos'] = lista
		else:
			dic_productos = {}
			dic_total = {}
			no_ventas = True

		ctx = {'reporte_productos' : dic_productos,
				'dic_total' : dic_total,
				'empresa_nombre' : empresa.nombre,
				'empresa_logo' : empresa.imagen_logo,
				'mes': mes,
				'anio' : date[0],
				'no_ventas' : no_ventas}

		template = get_template('pdf_mes_productos_vendidos.html')
		html = template.render(ctx)
		response = HttpResponse(content_type='application/pdf')  
		pisaStatus = pisa.CreatePDF(html,dest=response)
		return response

	else:
		return render(request,'mes_productos_vendidos.html')


@login_required
def modificar_img_empresa(request,id_empresa):
	avatar = Empresa.objects.get(pk=id_empresa) #Capturamos la informacion en una sola variable
	ret_data,errores = {},{}

	if request.method=='POST':
		if request.FILES.get('imagen') == None:
			errores['errores'] = "HAY ERRORES!" #Muestra un error si no se encuentra algun valor

		if not errores:
			try: 
				avatar.imagen_logo = request.FILES.get('imagen')
				avatar.save() 

			except Exception as e:	
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa')+"?error2") #Redireccionamiento que simula un refresh
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa')+"?ok2")		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa')+"?error2")
		
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa'))

def modificar_empresa(request,id_empresa):
	empresa = Empresa.objects.get(pk=id_empresa) #Capturamos la informacion en una sola variable
	ret_data,errores = {},{}
	if request.method=='POST':#usamos un metodo POST para recibir valores
		if request.POST.get('nombre') == '' or request.POST.get('telefono') == '' or request.POST.get('fecha_registro') == '' or request.POST.get('direccion') =='' or request.POST.get('latitude_empresa') =='' or request.POST.get('longitude_empresa') =='' or request.POST.get('correo') == '' or request.POST.get('descripcion') == '':
			errores['nombre'] = "HAY ERRORES!" #Muestra un error si no se encuentra algun valor
		if not errores:
			try: 
				empresa = Empresa.objects.filter(pk=id_empresa).update(
																			 nombre = request.POST.get('nombre'),
																			 telefono = request.POST.get('telefono'),
																			 fecha_registro = request.POST.get('fecha_registro'),	
																			 direccion = request.POST.get('direccion'),																			 
																			 latitude_empresa = request.POST.get('latitude_empresa'),
																			 longitude_empresa = request.POST.get('longitude_empresa'),	
																			 correo = request.POST.get('correo'),
																			 descripcion = request.POST.get('descripcion'),																			 
																			 ), #Actualizacion de datos
			except Exception as e: 
				print (e)
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa')+"?error")  #Redireccionamiento que simula un refresh
			else:
				return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa')+"?ok3")		
		else:
			return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa')+"?error")
	else:
		return HttpResponseRedirect(reverse('ecommerce_app:agregar_empresa'))

#Vista para el manejo de paginas no encontradas, renderiza a la vista principal que esta haga el trabajo
def error_404_view(request, exception):
	return redirect('ecommerce_app:principal')

#Se genera una factura, para la plantilla en administracion
def factura_orden(request, id):
	orden_factura = Orden.objects.filter(pk=id)
	fact = Orden.objects.get(pk=id)

	factura_detalle = DetalleOrden.objects.filter(orden=fact)

	cliente = Cliente.objects.filter(usuario_cliente=fact.usuario)
	empresa = Empresa.objects.filter(pk=1)
	logo_emp = Empresa.objects.get(pk=1)

	lista = []
	dic_data = {}

	for fact_det in factura_detalle:
		lista_data_prod = []
		lista_data_prod.append(fact_det.cantidad)
		lista_data_prod.append(fact_det.producto.nombre_producto)
		lista_data_prod.append(f'Lps {fact_det.producto.precio}')
		lista_data_prod.append(f'Lps {fact_det.descuento}')
		lista_data_prod.append(f'Lps {fact_det.total_producto}')

		lista.append(lista_data_prod)

	dic_data['detalle'] = lista

	ctx = {
			'factura' : dic_data,
			'cliente' : cliente,
			'orden_factura' : orden_factura,
			'empresa' : empresa,
			'logo_emp' : logo_emp.imagen_logo
		}

	template = get_template('factura_cliente.html')
	html = template.render(ctx)
	response = HttpResponse(content_type='application/pdf')  
	pisaStatus = pisa.CreatePDF(html,dest=response)
	return response


