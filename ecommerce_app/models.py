from django.db import models
from django.contrib.auth.models import User
import sys
import importlib
importlib.reload(sys)
#sys.setdefaultencoding('utf8')

# Create your models here.


class Categoria(models.Model):## Seria bueno agregar campo de img para las categorias, igual para las sub
	"""docstring for Categoria"""
	descripcion_categoria = models.CharField(max_length=50)
	def __str__(self):
		return "{}-{}".format(self.pk,self.descripcion_categoria)

	#si pertenece a Tecnologia, Hogar, Juguetes
class SubCategoria(models.Model):
	"""docstring for Categoria"""
	descripcion_subcategoria = models.CharField(max_length=50)
	categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

	def __str__(self):
		return "{}-{}".format(self.pk,self.descripcion_subcategoria)

class Marca(models.Model):
	"""docstring for Marca"""
	descripcion_marca = models.CharField(max_length=50)
	subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE)

	def __str__(self):
		return "{}".format(self.descripcion_marca,self.subcategoria.descripcion_subcategoria)

#Femenino
#Masculino
#Indefinido 
class Genero(models.Model):#este modelo no solo sirve para el cliente, si no para los productos
	descripcion_genero = models.CharField(max_length=20)
	def __str__(self):
		return "{}-{} " .format(self.pk,self.descripcion_genero)

class MetodoPago(models.Model):
	descripcion_pago = models.CharField(max_length=20)
	def __str__(self):
		return "{}-{} " .format(self.pk,self.descripcion_pago)

class Domicilio(models.Model):
	direccion = models.TextField()
	usuario = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(self):
		return "{}-{} " .format(self.pk,self.direccion)

class Empresa(models.Model):
	nombre = models.CharField(max_length=200)
	imagen_logo = models.ImageField(upload_to='logo_empresa')#upload_to carga un archivo en MEDIA_ROOT creando una carpeta con el nombre entre comillas
	telefono = models.CharField(max_length=50, blank = False, null = False)
	fecha_registro = models.DateField(auto_now_add=True)
	direccion = models.TextField()
	latitude_empresa = models.CharField(max_length=30,null=False)
	longitude_empresa = models.CharField(max_length=30,null=False)
	url_facebook = models.CharField(max_length=100,blank=True,null=True)
	url_instagram = models.CharField(max_length=100,blank=True,null=True)
	correo = models.EmailField()
	descripcion = models.TextField(verbose_name='descripcion_empresa')#Si no se da el nombre detallado, Django lo creará automáticamente usando el nombre del atributo del campo, convirtiendo los guiones bajos en espacios
	
	
	def __str__(self):
		return "{}-{} " .format(self.nombre,self.telefono)

class Producto(models.Model): 
	imagen_producto = models.ImageField(upload_to='imagen_producto')
	nombre_producto = models.CharField(max_length=200,blank=True,null=True)
	# existencia = models.IntegerField(default=0,blank = True, null = True)
	descripcion_producto = models.CharField(max_length=500,blank=True,null=True)
	modelo = models.CharField(max_length=500,blank=True,null=True)
	fecha_registro = models.DateField(auto_now_add=True,blank=True,null=True)
	precio = models.FloatField(default=0,blank = True, null = True)
	porcentaje_descuento = models.IntegerField(default=0,blank = True, null = True)
	esta_descuento = models.BooleanField(default = False)
	nuevo_producto = models.BooleanField(default = True)
	estado_producto = models.BooleanField(default = True)
	proveedor = models.CharField(max_length=500,blank=True,null=True)
	marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
	categoria_genero = models.ForeignKey(Genero, on_delete=models.CASCADE)#para diferenciar si un producto es para hombre u mujer, esto hara mas facil un filtro u para el buscador


	def __str__(self):
		return "{}-{}" .format(self.pk,self.nombre_producto)
#Cambiar el precio del producto, en caso haya descuento o este en promocion, precio anterior, precio actual
class Carrito(models.Model):
	"""docstring for lote"""
	
	cantidad = models.DecimalField(max_digits=10,decimal_places=2, null=True)
	producto =  models.ForeignKey(Producto, on_delete=models.CASCADE)
	usuario = models.ForeignKey(User,on_delete=models.CASCADE, null=True)

	def __str__(self):
		return "{}-{} |{}".format(self.pk,self.cantidad,self.producto.nombre_producto)

class Lote(models.Model):
	"""docstring for lote"""
	existencia = models.CharField(max_length=50)
	producto =  models.ForeignKey(Producto, on_delete=models.CASCADE)
	def __str__(self):
		return "{}-{} |{}".format(self.pk,self.existencia,self.producto.nombre_producto)
#opcional,  dejar en los datos de la empresa

class Orden(models.Model):
	fecha_compra = models.DateField(auto_now_add=True)
	total = models.DecimalField(max_digits=10,decimal_places=2, null=True)
	metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE)
	domicilio = models.ForeignKey(Domicilio, on_delete=models.CASCADE)
	usuario = models.ForeignKey(User, on_delete=models.CASCADE)
	descuento = models.DecimalField(max_digits=10,decimal_places=2, null=True)
	impuesto = models.DecimalField(max_digits=10,decimal_places=2, null=True)
	subtotal = models.DecimalField(max_digits=10,decimal_places=2, null=True)

	def __str__(self):
		return "{}-{} " .format(self.pk,self.total)

class DetalleOrden(models.Model):
	cantidad = models.IntegerField()
	precio = models.DecimalField(max_digits=10,decimal_places=2)
	producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
	orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
	total_producto = models.DecimalField(max_digits=10,decimal_places=2, null=True)

	def __str__(self):
		return "{}-{} |{} " .format(self.pk,self.cantidad,self.precio,self.producto.nombre_producto)


# Modelo cliente
class Cliente(models.Model):
	num_identidad = models.CharField(max_length=20)
	nombres =models.CharField(max_length=100)
	apellidos =models.CharField(max_length=100)
	genero = models.ForeignKey(Genero, on_delete=models.CASCADE)
	numero_telefono = models.CharField(max_length=50)
	fecha_nacimiento = models.DateField(auto_now_add=False)
	fecha_registro = models.DateField(auto_now_add=True)
	correo = models.CharField(max_length=100,blank=True,null=True)
	imagen = models.ImageField(upload_to='avatar',blank=True,null=True)
	usuario_cliente = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(self):
		return "{}-{} |{}".format(self.nombres,self.apellidos,self.usuario_cliente.username)



#Modelos restantes
#detalle_venta
#carrito
#cliente
#metodo_envio 'empresa, terceros, cliente'
#Marcas,Modelo , Proveedores
#Alertas ''

####cosas geniales ### likes por productos, asi poder mostrarlo en el dashboard, comentarios del producto, productos relacionados
##mapita de la empresa



#Datos de Telegram, trabajar con un chat-id o con group-id
class Telegram(models.Model):
	token = models.CharField(max_length=200)
	groupid = models.CharField(max_length=200)

	def __str__(self):
		return "{}" .format(self.pk)



