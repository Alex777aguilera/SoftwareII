from ecommerce_app.models import *


def ctx_base_cliente(request):
	categorias = Categoria.objects.all()
	empresa = Empresa.objects.get(pk=1)
	return {'ctx_categorias':categorias,
			'ctx_empresa':empresa}