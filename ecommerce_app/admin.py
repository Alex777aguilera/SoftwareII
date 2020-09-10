from django.contrib import admin

# Register your models here.
from django.apps import apps

myapp = apps.get_app_config("ecommerce_app")

for model_name, model in myapp.models.items():
	admin.site.register(model)