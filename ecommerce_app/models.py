from django.db import models
from django.contrib.auth.models import User
import sys
import importlib
importlib.reload(sys)
#sys.setdefaultencoding('utf8')

# Create your models here.

class TipoProducto(models.Model):
	descripcion_tipo_producto = models.CharField(max_length=100)
	
	def __str__(self):
		return "{}-{} " .format(self.pk,self.descripcion_tipo_producto)
    #Si el producto es nuevo,usado,especial
    #para colocoarlo en el buscador y filtrar por tipo de productos, sea promociones, descuentos, remates ect

class Categoria(models.Model):
	"""docstring for Categoria"""
	descripcion_categoria = models.CharField(max_length=50)
	def __str__(self):
		return "{}".format(self.pk,self.descripcion_categoria)
	#si pertenece a Tecnologia, Hogar, Juguetes

class Marca(models.Model):
	"""docstring for Marca"""
	descripcion_marca = models.CharField(max_length=50)
	def __str__(self):
		return "{}".format(self.pk,self.descripcion_marca)

class Modelo(models.Model):
	"""docstring for Modelo"""
	descripcion_modelo = models.CharField(max_length=50)
	def __str__(self):
		return "{}".format(self.pk,self.descripcion_modelo)

class MarcaModelo(models.Model):
	"""docstring for Modelo"""
	descripcion_marca_modelo = models.CharField(max_length=50)
	def __str__(self):
		return "{}".format(self.pk,self.descripcion_marca_modelo)

class TipoInventario(models.Model):
	tipo_inventario = models.CharField(max_length=200,blank=True,null=True)

	def __str__(self):
		return "{}".format(self.pk,self.tipo_inventario)
    #con inventario, significa que cuando se haga la compra se tiene que rebajar existencia
    #sin inventairo
   

class Empresa(models.Model):
	nombre = models.CharField(max_length=200)
	imagen_logo = models.ImageField(upload_to='logo_empresa')#upload_to carga un archivo en MEDIA_ROOT creando una carpeta con el nombre entre comillas
	contacto = models.CharField(max_length=20)
	correo = models.CharField(max_length=100)
	fecha_registro = models.DateField(auto_now_add=True)
	direccion = models.TextField()
	#direccion_gps = models.TextField(blank = True, null = True)
	latitude_empresa = models.FloatField(default = 0.00, blank = True, null = True)
	longitude_empresa = models.FloatField(default = 0.00, blank = True, null = True)
	descripcion = models.TextField(verbose_name='descripcion_empresa')#Si no se da el nombre detallado, Django lo creará automáticamente usando el nombre del atributo del campo, convirtiendo los guiones bajos en espacios
	#encargado = models.ForeignKey(#)
	
	def __str__(self):
		return "{} {} " .format(self.nombre,self.contacto)

class Producto(models.Model):
	imagen_producto = models.ImageField(upload_to='imagen_producto')
	nombre_producto = models.CharField(max_length=200,blank=True,null=True)
	descripcion_producto = models.CharField(max_length=500,blank=True,null=True)
	fecha_registro = models.DateField(auto_now_add=True,blank=True,null=True)
	precio = models.FloatField(default=0,blank = True, null = True)
	porcentaje_descuento = models.IntegerField(default=0,blank = True, null = True)
	esta_descuento = models.BooleanField(default = False)
	nuevo_producto = models.BooleanField(default = False)
	proveedor = models.CharField(max_length=500,blank=True,null=True)
	tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
	categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
	marca_modelo = models.ForeignKey(MarcaModelo, on_delete=models.CASCADE)

	def __str__(self):
		return "{}-{} " .format(self.pk,self.nombre_producto,self.categoria)

class Carrito(models.Model):
	"""docstring for lote"""
	cantidad = models.CharField(max_length=50)
	producto =  models.ForeignKey(Producto, on_delete=models.CASCADE)
	usuario = models.ForeignKey(User,on_delete=models.CASCADE, null=True)

	def __str__(self):
		return "{}".format(self.pk,self.cantidad,self.producto)

class Lote(models.Model):
	"""docstring for lote"""
	existencia = models.CharField(max_length=50)
	producto =  models.ForeignKey(Producto, on_delete=models.CASCADE)
	def __str__(self):
		return "{}".format(self.pk,self.existencia,self.producto)
#opcional,  dejar en los datos de la empresa
class Redes_sociales(models.Model):
	url_facebook = models.CharField(max_length=100,blank=True,null=True)
	url_instagram = models.CharField(max_length=100,blank=True,null=True)
	correo = models.EmailField()
	def __str__(self):
		return "{}".format(self.pk)

class Venta(models.Model):
	cantidad = models.IntegerField()
	producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

	#descripcion_producto
	def __str__(self):
		return "{}-{} " .format(self.pk,self.nombre_producto,self.cantidad)

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


