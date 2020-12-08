from ecommerce_app.models import *


def ctx_base_cliente(request):
	categorias = Categoria.objects.all()
	subcategorias = SubCategoria.objects.filter().order_by('-id')[:4]
	empresa = Empresa.objects.get(pk=1)
	productos = Producto.objects.filter(esta_descuento = True).order_by('-id')[:8]
	return {'ctx_categorias':categorias,
			'ctx_empresa':empresa,
			'ctx_productos_descuento':productos,
			'ctx_subcategorias':subcategorias}